from dataclasses import replace
import pytest
from backend.digital_human.video.models import *
from backend.digital_human.video.evaluation import *
from backend.digital_human.video.providers import *
from backend.digital_human.video.services import *
from backend.digital_human.video.benchmark import AIRA_VIDEO_BENCHMARK_V1

def fixtures():
    motion=MotionProfile("AIRA", "1")
    expression=ExpressionProfile(ExpressionName.SOFT_SMILE, "friendly", 35)
    scene=SceneProfile("STUDIO", "day", "soft", "minimal")
    camera=CameraProfile("medium", 50, "eye", "1m", "centered")
    request=VideoGenerationRequest("AIRA","AIRA_DIGITAL_HUMAN_V1","s1","Approved words","speech1","visual1","voice1",motion,expression,scene,camera,"AIRA_REELS",30,"9:16",("safe",),("master",),10)
    lock=VideoIdentityLock("visual1","voice1")
    asset=VideoAsset("AIRA","AIRA_DIGITAL_HUMAN_V1",request.request_id,"safe","v1","s1","speech1",("master",),motion.motion_profile_id,expression.expression_id,scene.scene_id,camera,95,94,90,92,93,94,"APPROVED","PENDING","store://raw","abc",30)
    return request, lock, asset

def test_profiles_validate_ranges():
    with pytest.raises(ValueError): MotionProfile("AIRA","1",energy_level=101)
    with pytest.raises(ValueError): ExpressionProfile(ExpressionName.NEUTRAL,"neutral",-1)
    with pytest.raises(ValueError): LipSyncProfile("v1","ru","p","safe",timing_offset_ms=1001)

def test_request_character_identity_is_locked():
    request,_,_=fixtures()
    with pytest.raises(ValueError): replace(request, character_id="Founder")

def test_temporal_identity_detects_single_frame_and_eye_drift():
    _,lock,_=fixtures()
    result=evaluate_temporal_identity([(0,95),(20,94),(40,81),(60,76)],lock,20)
    assert not result.passed and result.minimum_score == 76
    assert result.temporal_identity_score < 90
    assert ArtifactType.IDENTITY_DRIFT in {a.type for a in result.artifacts}

def test_lipsync_offset_fails_and_metrics_stay_separate():
    result=evaluate_lipsync(lip_timing_accuracy=95,phoneme_match=95,pause_match=95,jaw_stability=95,
        lip_shape_naturalness=95,face_identity_preservation=95,audio_delay_ms=0,visual_delay_ms=120)
    assert not result.passed and "OUT_OF_SYNC" in result.failures

class FakeProvider(VideoGenerationProvider):
    def __init__(self,cost=5,healthy=True): self.cost=cost; self.healthy=healthy
    def generate_video(self,request): return "job"
    def get_capabilities(self): return frozenset({ProviderCapability.VIDEO_FROM_IMAGE,ProviderCapability.REFERENCE_IDENTITY})
    def estimate_cost(self,request): return self.cost
    def health_check(self): return self.healthy

def test_router_denies_unapproved_master_reference_and_obeys_budget():
    request,_,_=fixtures()
    bad=ProviderRecord("safe",FakeProvider(),False,100,100,100,100,100,100)
    with pytest.raises(LookupError): VideoProviderRouter([bad]).route(request,{ProviderCapability.VIDEO_FROM_IMAGE})
    expensive=ProviderRecord("safe",FakeProvider(11),True,100,100,100,100,100,100)
    with pytest.raises(LookupError): VideoProviderRouter([expensive]).route(request,{ProviderCapability.VIDEO_FROM_IMAGE})

def test_router_prioritizes_identity_and_privacy():
    request,_,_=fixtures()
    low=ProviderRecord("safe",FakeProvider(),True,70,99,99,99,70,100)
    high=ProviderRecord("better",FakeProvider(),True,99,90,90,80,99,100)
    request=replace(request,provider_policy=("safe","better"))
    assert VideoProviderRouter([low,high]).route(request,{ProviderCapability.REFERENCE_IDENTITY}).name == "better"

def test_asset_lineage_is_non_destructive():
    _,_,asset=fixtures(); derived=asset.derive(file_reference="store://captioned",hash="def")
    assert derived.parent_asset_id == asset.asset_id and derived.asset_id != asset.asset_id
    assert asset.file_reference == "store://raw"

def test_segments_and_project_order():
    project=VideoProject("short")
    b=VideoSegment(project.project_id,1,"Demo",15,"scene","demo",None,"broll",None)
    a=VideoSegment(project.project_id,0,"Hook",3,"scene","hook","speech","aira","motion")
    project.add_segment(b); project.add_segment(a)
    assert [s.purpose for s in project.segments] == ["Hook","Demo"]
    with pytest.raises(ValueError): project.add_segment(replace(a,segment_id=identifier()))

def test_guardian_rejects_beautiful_wrong_face_voice_and_words():
    _,lock,asset=fixtures()
    lips=evaluate_lipsync(lip_timing_accuracy=95,phoneme_match=95,pause_match=95,jaw_stability=95,lip_shape_naturalness=95,face_identity_preservation=95,audio_delay_ms=0,visual_delay_ms=0)
    motion=evaluate_motion(95,95,95,95); guardian=VideoGuardian()
    drift=evaluate_temporal_identity([(0,95),(30,70)],lock)
    assert guardian.review(asset,lock,drift,lips,motion,True,True)==VideoStatus.REJECTED_IDENTITY
    stable=evaluate_temporal_identity([(0,95),(30,94)],lock)
    assert guardian.review(asset,lock,stable,lips,motion,True,False)==VideoStatus.REJECTED_VOICE_IDENTITY
    assert guardian.review(asset,lock,stable,lips,motion,False,True)==VideoStatus.REJECTED_LIPSYNC

def test_founder_is_final_authority_and_publication_requires_both():
    _,_,asset=fixtures()
    feedback=FounderFeedback(asset.asset_id,"TOO_ROBOTIC","Движения выглядят не как AIRA.")
    assert apply_founder_feedback(asset,feedback)==VideoStatus.REJECTED_MOTION_IDENTITY
    assert not can_publish(replace(asset,status=VideoStatus.APPROVED,founder_status="PENDING"))
    assert can_publish(replace(asset,status=VideoStatus.APPROVED,founder_status="APPROVED"))

def test_security_budget_transcript_and_benchmark():
    with pytest.raises(SecurityError): authorize_reference_upload(False,True)
    ledger=BudgetLedger(10,20,30)
    assert ledger.authorize(11)==VideoStatus.WAITING_FOUNDER_APPROVAL
    assert ledger.authorize(5) is None
    assert transcript_matches("Approved  words", "approved words")
    assert not transcript_matches("approved words", "changed words")
    assert len(AIRA_VIDEO_BENCHMARK_V1.scenarios)==12
