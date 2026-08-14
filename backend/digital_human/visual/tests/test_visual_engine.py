from dataclasses import replace

import pytest

from backend.digital_human.identity import aira_visual_identity_pack_v1, register_master_reference
from backend.digital_human.visual.domain import *
from backend.digital_human.visual.engine import BudgetApprovalRequired, DigitalHumanEngine
from backend.digital_human.visual.evaluation import ThresholdGuardian
from backend.digital_human.visual.prompts import VisualPromptBuilder
from backend.digital_human.visual.providers import ProviderCapabilities, ProviderOutput, VisualModelRouter
from backend.digital_human.visual.repository import AssetRepository, IdentityRepository, ProtectionError, ReferenceRepository


def master():
    return register_master_reference("asset://protected/aira/master/v1", "a" * 64)


def request(cost=10):
    return VisualGenerationRequest(
        "req-1", "AIRA", "1.0", "Instagram Post", "Instagram Feed", "minimal home workspace",
        Wardrobe("white shirt", "white"), "working at laptop", Expression.FOCUSED,
        Camera("portrait", "eye level", "50mm", "eye level", "vertical", "natural", "medium", "still", "4:5"),
        "natural window light", "4:5", ("AIRA_MASTER_REFERENCE_V1",), "aira_lifestyle",
        ProviderPolicy(frozenset({"PHOTOREALISM", "IDENTITY_REFERENCE"})), 1, cost)


class FakeProvider:
    provider_id = "safe-provider"
    founder_approved = True
    data_retention_policy = "no retention"
    training_usage_policy = "no training"
    def get_capabilities(self): return ProviderCapabilities(frozenset({"PHOTOREALISM", "IDENTITY_REFERENCE"}), "2048x2048")
    def estimate_cost(self, request): return 5
    def health_check(self): return True
    def generate_image(self, request, prompt): return [ProviderOutput("candidate-1", "model-v1", "asset://candidate/1", "b" * 64)]
    def edit_image(self, source_file_reference, prompt): raise NotImplementedError
    def generate_variations(self, source_file_reference, count): raise NotImplementedError


class Evaluator:
    def __init__(self, identity=96, quality=92): self.result = EvaluationResult(identity, quality)
    def evaluate(self, asset): return self.result


def test_identity_profile_and_only_one_active_identity():
    profile = aira_visual_identity_pack_v1(master())
    repo = IdentityRepository(); repo.save(profile)
    with pytest.raises(ValueError, match="only one"):
        repo.save(replace(profile, identity_id="other"))
    with pytest.raises(ValueError, match="Founder"):
        replace(profile, founder_approved=False)


def test_reference_hierarchy_master_protection_and_founder_promotion():
    repo = ReferenceRepository(); repo.register(master())
    with pytest.raises(ProtectionError): repo.register(master())
    with pytest.raises(ProtectionError): repo.delete("AIRA_MASTER_REFERENCE_V1", founder_workflow_approved=True)
    generated = AssetReference("candidate", "asset://candidate", "b" * 64, ReferenceLevel.GENERATED_CONTENT, False)
    repo.register(generated)
    with pytest.raises(ProtectionError): repo.promote("candidate", founder_id=None)
    assert repo.promote("candidate", founder_id="founder").level is ReferenceLevel.FOUNDER_APPROVED_REFERENCE


def test_generation_request_and_prompt_layers():
    profile = aira_visual_identity_pack_v1(master())
    lock = IdentityLock((profile.master_reference_id,), ("preserve facial geometry",))
    prompt = VisualPromptBuilder().build(profile, lock, request())
    positions = [prompt.text.index(f"[{layer}]") for layer in VisualPromptBuilder.ORDER]
    assert positions == sorted(positions)
    assert "blue eyes" in prompt.text and "do not change identity" in prompt.text
    with pytest.raises(ValueError, match="aspect"):
        replace(request(), aspect_ratio="3:2")


def test_router_generation_evaluation_guardian_and_founder_override():
    profile = aira_visual_identity_pack_v1(master()); assets = AssetRepository()
    engine = DigitalHumanEngine(VisualModelRouter([FakeProvider()]), Evaluator(), ThresholdGuardian(), assets)
    generated = engine.generate(request(), profile, IdentityLock((profile.master_reference_id,), ("face",)))[0]
    assert generated.status is AssetStatus.FOUNDER_REVIEW
    rejected = engine.founder_decision(generated, approved=False)
    assert rejected.status is AssetStatus.REJECTED_IDENTITY and not rejected.disclosure.founder_approved


@pytest.mark.parametrize("identity,quality,status", [(68, 99, AssetStatus.REJECTED_IDENTITY), (95, 60, AssetStatus.REJECTED_QUALITY)])
def test_beautiful_wrong_identity_and_independent_quality(identity, quality, status):
    profile = aira_visual_identity_pack_v1(master())
    engine = DigitalHumanEngine(VisualModelRouter([FakeProvider()]), Evaluator(identity, quality), ThresholdGuardian(), AssetRepository())
    assert engine.generate(request(), profile, IdentityLock((profile.master_reference_id,), ("face",)))[0].status is status


def test_lineage_is_non_destructive_and_budget_waits_for_founder():
    profile = aira_visual_identity_pack_v1(master()); assets = AssetRepository()
    engine = DigitalHumanEngine(VisualModelRouter([FakeProvider()]), Evaluator(), ThresholdGuardian(), assets, daily_budget=4)
    with pytest.raises(BudgetApprovalRequired, match="WAITING_FOUNDER_APPROVAL"):
        engine.generate(request(), profile, IdentityLock((profile.master_reference_id,), ("face",)))
    engine = DigitalHumanEngine(VisualModelRouter([FakeProvider()]), Evaluator(), ThresholdGuardian(), assets)
    original = engine.generate(request(), profile, IdentityLock((profile.master_reference_id,), ("face",)))[0]
    edited = original.edited_copy("asset://candidate/2", "c" * 64, "background replacement")
    assets.save(edited)
    assert edited.parent_asset_id == original.asset_id and assets.items[original.asset_id].file_reference != edited.file_reference


def test_provider_replacement_preserves_identity_above_provider():
    profile = aira_visual_identity_pack_v1(master())
    second = FakeProvider(); second.provider_id = "replacement"
    second.estimate_cost = lambda request: 4
    asset = DigitalHumanEngine(VisualModelRouter([FakeProvider(), second]), Evaluator(), ThresholdGuardian(), AssetRepository()).generate(
        request(), profile, IdentityLock((profile.master_reference_id,), ("face",)))[0]
    assert asset.provider == "replacement" and asset.reference_ids == (profile.master_reference_id,)
