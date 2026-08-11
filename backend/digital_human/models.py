"""Core immutable-ish records and policies for AIRA's visual identity."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IdentityStatus(str, Enum):
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    FOUNDER_REVIEW = "FOUNDER_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class ReferenceLevel(int, Enum):
    MASTER_REFERENCE = 1
    FOUNDER_APPROVED_REFERENCE = 2
    IDENTITY_TEST_REFERENCE = 3
    GENERATED_CONTENT = 4


class AssetStatus(str, Enum):
    GENERATED = "GENERATED"
    EVALUATING = "EVALUATING"
    REJECTED_IDENTITY = "REJECTED_IDENTITY"
    REJECTED_QUALITY = "REJECTED_QUALITY"
    GUARDIAN_REVIEW = "GUARDIAN_REVIEW"
    FOUNDER_REVIEW = "FOUNDER_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    WAITING_FOUNDER_APPROVAL = "WAITING_FOUNDER_APPROVAL"


class Expression(str, Enum):
    NEUTRAL = "NEUTRAL"
    SOFT_SMILE = "SOFT_SMILE"
    CONFIDENT = "CONFIDENT"
    CURIOUS = "CURIOUS"
    FOCUSED = "FOCUSED"
    FRIENDLY = "FRIENDLY"
    THOUGHTFUL = "THOUGHTFUL"
    SURPRISED_SUBTLE = "SURPRISED_SUBTLE"


@dataclass(frozen=True)
class AssetReference:
    asset_id: str
    storage_uri: str
    sha256: str
    level: ReferenceLevel
    founder_approved: bool = False
    read_only: bool = False
    parent_asset_id: str | None = None

    def __post_init__(self) -> None:
        if not self.storage_uri.startswith(("asset://", "s3://", "gs://", "file://")):
            raise ValueError("reference must use the Asset Storage abstraction")
        if self.level in {ReferenceLevel.MASTER_REFERENCE, ReferenceLevel.FOUNDER_APPROVED_REFERENCE} and not self.founder_approved:
            raise ValueError("canonical references require Founder approval")
        if self.level is ReferenceLevel.MASTER_REFERENCE and not self.read_only:
            raise ValueError("master references are read-only")


@dataclass(frozen=True)
class FaceProfile:
    reference_ids: tuple[str, ...]
    attributes: tuple[str, ...]
    evaluation_data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HairProfile:
    color_family: str = "blonde / light blonde"
    length: str = "long"
    baseline_style: str = "loose natural waves"
    texture: str = "natural"
    volume: str = "medium / high"


@dataclass(frozen=True)
class EyeProfile:
    color: str = "blue"
    priority: str = "CRITICAL"


@dataclass(frozen=True)
class SkinProfile:
    tone: str = "light"
    texture: str = "natural photorealistic texture"
    retouching: str = "minimal"


@dataclass(frozen=True)
class MakeupProfile:
    default: str = "natural, clean, refined"
    lashes: str = "defined"
    brows: str = "natural and balanced"
    lips: str = "soft natural"


@dataclass(frozen=True)
class BrandProfile:
    qualities: tuple[str, ...] = ("photorealistic", "modern", "clean", "premium", "natural", "approachable", "minimalistic")
    palette: tuple[str, ...] = ("white", "neutral gray", "soft black", "soft violet", "controlled burgundy")
    signature_look: str = "white relaxed shirt, natural blonde hair, blue eyes, minimal jewelry, modern workspace, soft violet accent"


@dataclass(frozen=True)
class IdentityLock:
    canonical_reference_ids: tuple[str, ...]
    face_constraints: tuple[str, ...]
    eye_constraints: tuple[str, ...] = ("blue eyes", "preserve eye shape")
    hair_constraints: tuple[str, ...] = ("blonde/light blonde family", "preserve hairline")
    skin_constraints: tuple[str, ...] = ("light tone", "natural texture", "no plastic smoothing")
    age_consistency: str = "stable young-adult appearance"
    body_constraints: tuple[str, ...] = ()
    strength_policy: str = "identity has priority over aesthetics"

    def __post_init__(self) -> None:
        if not self.canonical_reference_ids:
            raise ValueError("IdentityLock requires a canonical reference")


@dataclass
class VisualIdentityProfile:
    identity_id: str
    character_id: str
    name: str
    version: str
    status: IdentityStatus
    founder_approved: bool
    master_reference: AssetReference
    reference_set: list[AssetReference]
    face_profile: FaceProfile
    hair_profile: HairProfile = field(default_factory=HairProfile)
    eye_profile: EyeProfile = field(default_factory=EyeProfile)
    skin_profile: SkinProfile = field(default_factory=SkinProfile)
    body_profile: dict[str, Any] = field(default_factory=dict)
    makeup_profile: MakeupProfile = field(default_factory=MakeupProfile)
    brand_profile: BrandProfile = field(default_factory=BrandProfile)
    wardrobe_rules: tuple[str, ...] = ("prefer white/light minimal clothing", "use controlled wardrobe families")
    allowed_variation: tuple[str, ...] = ("scene", "pose", "expression", "lighting", "camera", "hairstyle")
    forbidden_variation: tuple[str, ...] = ("identity", "eye color", "hair color family", "material age drift")
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.master_reference.level is not ReferenceLevel.MASTER_REFERENCE:
            raise ValueError("master_reference has incorrect hierarchy level")
        if self.status in {IdentityStatus.APPROVED, IdentityStatus.ACTIVE} and not self.founder_approved:
            raise ValueError("approved/active identities require Founder approval")


@dataclass(frozen=True)
class CameraSpec:
    shot_type: str
    angle: str = "eye level"
    lens_equivalent: str = "50mm"
    camera_height: str = "eye level"
    orientation: str = "portrait"
    depth_of_field: str = "natural"
    distance: str = "medium"
    motion: str = "still"
    aspect_ratio: str = "4:5"


@dataclass(frozen=True)
class WardrobeSpec:
    category: str
    color: str
    material: str = "natural fabric"
    fit: str = "relaxed"
    accessories: tuple[str, ...] = ()
    footwear: str | None = None
    brand_compatible: bool = True
    identity_compatible: bool = True


@dataclass(frozen=True)
class VisualGenerationRequest:
    request_id: str
    character_id: str
    identity_version: str
    purpose: str
    platform: str
    scene: str
    wardrobe: WardrobeSpec
    pose: str
    expression: Expression
    camera: CameraSpec
    lighting: str
    aspect_ratio: str
    reference_ids: tuple[str, ...]
    task_profile: str
    provider_policy: str
    candidate_count: int = 4
    cost_limit: float = 10.0
    founder_approval_required: bool = True

    def __post_init__(self) -> None:
        if self.aspect_ratio not in {"9:16", "4:5", "1:1", "16:9"}:
            raise ValueError("unsupported aspect ratio")
        if not 1 <= self.candidate_count <= 16 or self.cost_limit < 0:
            raise ValueError("invalid candidate count or cost limit")
        if not self.reference_ids:
            raise ValueError("generation requires identity references")


@dataclass
class VisualAsset:
    asset_id: str
    character_id: str
    identity_version: str
    generation_request_id: str
    provider: str
    model: str
    prompt_version: str
    reference_ids: tuple[str, ...]
    scene: str
    wardrobe: WardrobeSpec
    pose: str
    expression: Expression
    camera: CameraSpec
    lighting: str
    file_reference: str
    sha256: str
    parent_asset_id: str | None = None
    identity_score: float | None = None
    quality_score: float | None = None
    guardian_status: str = "PENDING"
    founder_status: str = "PENDING"
    usage_rights_metadata: dict[str, Any] = field(default_factory=dict)
    disclosure: dict[str, Any] = field(default_factory=lambda: {"generated_by_ai": True, "edited_by_ai": False, "human_reviewed": False, "founder_approved": False, "platform_disclosure_required": False, "disclosure_applied": False})
    status: AssetStatus = AssetStatus.GENERATED
    created_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True)
class VisualFeedback:
    target_asset_id: str
    category: str
    severity: str
    reason: str
    founder_decision: str
    created_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True)
class DigitalHumanProfile:
    character_id: str
    visual_identity_id: str
    behavior_profile_id: str
    core_identity_id: str
    voice_profile_id: str | None = None
    motion_profile_id: str | None = None


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"
