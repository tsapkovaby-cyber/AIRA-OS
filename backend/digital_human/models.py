"""Provider-neutral domain records for motion, lip-sync and video."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def now() -> datetime:
    return datetime.now(timezone.utc)


def identifier() -> str:
    return str(uuid4())


def score(value: float, name: str = "score") -> float:
    if not 0 <= value <= 100:
        raise ValueError(f"{name} must be between 0 and 100")
    return value


class MotionMode(StrEnum):
    NEUTRAL_STANDING="NEUTRAL_STANDING"; NEUTRAL_SITTING="NEUTRAL_SITTING"
    SPEAKING_CAMERA="SPEAKING_CAMERA"; EXPLAINING="EXPLAINING"; LISTENING="LISTENING"
    THOUGHTFUL="THOUGHTFUL"; FRIENDLY="FRIENDLY"; PRESENTING_OBJECT="PRESENTING_OBJECT"
    WORKING="WORKING"; WALKING="WALKING"; SHORT_FORM_DYNAMIC="SHORT_FORM_DYNAMIC"
    LONG_FORM_CALM="LONG_FORM_CALM"


class ExpressionName(StrEnum):
    NEUTRAL="NEUTRAL"; SOFT_SMILE="SOFT_SMILE"; FRIENDLY="FRIENDLY"; CURIOUS="CURIOUS"
    FOCUSED="FOCUSED"; THOUGHTFUL="THOUGHTFUL"; CONFIDENT="CONFIDENT"
    EXCITED_SUBTLE="EXCITED_SUBTLE"; SERIOUS="SERIOUS"


class VideoStatus(StrEnum):
    GENERATED="GENERATED"; PROCESSING="PROCESSING"; EVALUATING="EVALUATING"
    REJECTED_IDENTITY="REJECTED_IDENTITY"; REJECTED_VOICE_IDENTITY="REJECTED_VOICE_IDENTITY"
    REJECTED_MOTION="REJECTED_MOTION"; REJECTED_MOTION_IDENTITY="REJECTED_MOTION_IDENTITY"
    REJECTED_LIPSYNC="REJECTED_LIPSYNC"; REJECTED_QUALITY="REJECTED_QUALITY"
    GUARDIAN_REVIEW="GUARDIAN_REVIEW"; FOUNDER_REVIEW="FOUNDER_REVIEW"
    APPROVED="APPROVED"; PUBLISHED="PUBLISHED"; ARCHIVED="ARCHIVED"
    WAITING_FOUNDER_APPROVAL="WAITING_FOUNDER_APPROVAL"


class ArtifactType(StrEnum):
    FACE_WARP="FACE_WARP"; HAND_ERROR="HAND_ERROR"; BODY_WARP="BODY_WARP"
    HAIR_ERROR="HAIR_ERROR"; CLOTHING_CHANGE="CLOTHING_CHANGE"; BACKGROUND_MORPH="BACKGROUND_MORPH"
    OBJECT_MORPH="OBJECT_MORPH"; LIP_SYNC_ERROR="LIP_SYNC_ERROR"; EYE_DRIFT="EYE_DRIFT"
    TEETH_ERROR="TEETH_ERROR"; FRAME_FLICKER="FRAME_FLICKER"; IDENTITY_DRIFT="IDENTITY_DRIFT"


class ProviderCapability(StrEnum):
    VIDEO_FROM_IMAGE="VIDEO_FROM_IMAGE"; VIDEO_FROM_TEXT="VIDEO_FROM_TEXT"
    REFERENCE_IDENTITY="REFERENCE_IDENTITY"; LIP_SYNC="LIP_SYNC"; MOTION_CONTROL="MOTION_CONTROL"
    CAMERA_CONTROL="CAMERA_CONTROL"; AUDIO_INPUT="AUDIO_INPUT"; LONG_VIDEO="LONG_VIDEO"
    SCENE_EXTENSION="SCENE_EXTENSION"; FRAME_INTERPOLATION="FRAME_INTERPOLATION"


@dataclass(frozen=True)
class BlinkProfile:
    average_frequency: float = 15
    allowed_range: tuple[float, float] = (8, 25)
    expression_modifier: float = 1; speaking_modifier: float = 1; stress_modifier: float = 1
    def __post_init__(self):
        if self.average_frequency <= 0 or self.allowed_range[0] > self.average_frequency or self.average_frequency > self.allowed_range[1]:
            raise ValueError("average blink frequency must be positive and within allowed range")


@dataclass(frozen=True)
class MotionProfile:
    character_id: str; version: str
    motion_profile_id: str = field(default_factory=identifier)
    body_movement_style: str = "calm, controlled, subtle, natural"
    head_movement_style: str = "small natural movements and occasional tilt"
    gesture_style: str = "low-to-medium subtle emphasis"
    eye_movement_style: str = "camera contact with brief natural gaze shifts"
    posture: str = "relaxed, upright, confident"
    energy_level: int = 35
    idle_motion: str = "subtle"; speaking_motion: str = "speech-supporting"
    walking_motion: str = "natural"; listening_motion: str = "attentive"
    expression_coupling: dict[str, int] = field(default_factory=dict)
    blink_profile: BlinkProfile = field(default_factory=BlinkProfile)
    founder_approval: bool = False; status: str = "DRAFT"
    created_at: datetime = field(default_factory=now); updated_at: datetime = field(default_factory=now)
    history: tuple[str, ...] = ()
    def __post_init__(self): score(self.energy_level, "energy_level")


@dataclass(frozen=True)
class ExpressionProfile:
    name: ExpressionName; emotion: str; intensity: int
    expression_id: str = field(default_factory=identifier)
    facial_parameters: dict[str, float] = field(default_factory=dict)
    eye_behavior: str = "natural"; brow_behavior: str = "subtle"; mouth_behavior: str = "natural"
    motion_compatibility: tuple[MotionMode, ...] = tuple(MotionMode)
    founder_approval: bool = False
    def __post_init__(self): score(self.intensity, "intensity")


@dataclass(frozen=True)
class LipSyncProfile:
    voice_identity_version: str; language: str; phoneme_model: str; provider: str
    sync_method: str = "phoneme"; timing_offset_ms: int = 0; quality_threshold: float = 85
    identity_safety: bool = True; founder_approval: bool = False
    def __post_init__(self):
        score(self.quality_threshold, "quality_threshold")
        if abs(self.timing_offset_ms) > 1000: raise ValueError("timing offset is unsafe")


@dataclass(frozen=True)
class SceneProfile:
    environment: str; time: str; lighting: str; background: str
    scene_id: str = field(default_factory=identifier); foreground: str = ""
    props: tuple[str, ...] = (); camera: str = ""; motion_constraints: tuple[str, ...] = ()
    brand_compatibility: tuple[str, ...] = (); platform_compatibility: tuple[str, ...] = ()


@dataclass(frozen=True)
class CameraProfile:
    shot_type: str; lens_equivalent_mm: int; camera_height: str; distance: str; framing: str
    movement: str = "STATIC"; stabilization: str = "stable"; focus: str = "face"
    depth_of_field: str = "natural"; aspect_ratio: str = "9:16"


@dataclass(frozen=True)
class VideoIdentityLock:
    visual_identity_version: str; voice_identity_version: str
    minimum_identity_score: float = 90; maximum_frame_drop: float = 8
    allowed_motion_modes: tuple[MotionMode, ...] = tuple(MotionMode)
    maximum_expression_intensity: int = 50; minimum_lipsync_score: float = 85
    canonical_references_immutable: bool = True
    def __post_init__(self):
        score(self.minimum_identity_score); score(self.minimum_lipsync_score)


@dataclass(frozen=True)
class VideoGenerationRequest:
    character_id: str; digital_human_version: str; script_id: str; approved_script: str
    speech_asset_id: str; visual_identity_version: str; voice_identity_version: str
    motion_profile: MotionProfile; expression_profile: ExpressionProfile; scene_profile: SceneProfile
    camera_profile: CameraProfile; platform_profile: str; duration_seconds: float; aspect_ratio: str
    provider_policy: tuple[str, ...]; reference_assets: tuple[str, ...]; cost_limit: float
    founder_approval_requirement: bool = True; request_id: str = field(default_factory=identifier)
    created_at: datetime = field(default_factory=now)
    def __post_init__(self):
        if not self.approved_script.strip() or self.duration_seconds <= 0 or self.cost_limit < 0: raise ValueError("invalid video request")
        if self.motion_profile.character_id != self.character_id: raise ValueError("motion profile belongs to another character")


@dataclass(frozen=True)
class VideoArtifact:
    type: ArtifactType; timestamp_seconds: float; frame_range: tuple[int, int]
    severity: int; likely_cause: str = ""; provider: str = ""; prompt: str = ""; motion_state: str = ""


@dataclass(frozen=True)
class VideoAsset:
    character_id: str; digital_human_version: str; generation_request_id: str; provider: str; model: str
    script_version: str; speech_asset_id: str; visual_references: tuple[str, ...]
    motion_profile_id: str; expression_profile_id: str; scene_profile_id: str; camera_profile: CameraProfile
    identity_score: float; temporal_identity_score: float; motion_score: float; lipsync_score: float
    quality_score: float; brand_score: float; guardian_status: str; founder_status: str
    file_reference: str; hash: str; duration_seconds: float; asset_id: str = field(default_factory=identifier)
    created_at: datetime = field(default_factory=now); parent_asset_id: str | None = None
    status: VideoStatus = VideoStatus.GENERATED; artifacts: tuple[VideoArtifact, ...] = ()
    def derive(self, *, file_reference: str, hash: str) -> "VideoAsset":
        return replace(self, asset_id=identifier(), parent_asset_id=self.asset_id, file_reference=file_reference,
                       hash=hash, created_at=now(), status=VideoStatus.PROCESSING)


@dataclass(frozen=True)
class VideoSegment:
    video_project_id: str; order: int; purpose: str; duration_seconds: float; scene_profile_id: str
    script_portion: str; speech_asset_id: str | None; visual_asset_id: str | None
    motion_profile_id: str | None; transition: str = "cut"; status: str = "DRAFT"
    segment_id: str = field(default_factory=identifier)
    def __post_init__(self):
        if self.order < 0 or self.duration_seconds <= 0: raise ValueError("invalid segment")


@dataclass
class VideoProject:
    title: str; project_id: str = field(default_factory=identifier); segments: list[VideoSegment] = field(default_factory=list)
    status: str = "DRAFT"
    def add_segment(self, segment: VideoSegment) -> None:
        if segment.video_project_id != self.project_id: raise ValueError("segment belongs to another project")
        if any(s.order == segment.order for s in self.segments): raise ValueError("duplicate segment order")
        self.segments.append(segment); self.segments.sort(key=lambda s: s.order)


@dataclass(frozen=True)
class DigitalHumanProfile:
    profile_id: str; core_identity_version: str; visual_identity_version: str; voice_identity_version: str
    motion_profile_id: str; expression_profile_id: str; lipsync_profile_version: str; behavior_profile_version: str


@dataclass(frozen=True)
class FounderFeedback:
    asset_id: str; category: str; comment: str; accepted: bool = False; created_at: datetime = field(default_factory=now)


@dataclass(frozen=True)
class VideoDisclosure:
    provider: str; generated_video: bool = True; generated_voice: bool = True; digital_character: str = "AIRA"
    human_reviewed: bool = False; founder_approved: bool = False
    disclosure_required: bool = True; disclosure_applied: bool = False
