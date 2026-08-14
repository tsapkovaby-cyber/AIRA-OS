"""Sprint 018 domain model. Identity data is intentionally provider independent."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IdentityStatus(StrEnum):
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    FOUNDER_REVIEW = "FOUNDER_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class ReferenceLevel(StrEnum):
    MASTER_REFERENCE = "MASTER_REFERENCE"
    FOUNDER_APPROVED_REFERENCE = "FOUNDER_APPROVED_REFERENCE"
    IDENTITY_TEST_REFERENCE = "IDENTITY_TEST_REFERENCE"
    GENERATED_CONTENT = "GENERATED_CONTENT"


class AssetStatus(StrEnum):
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


class Expression(StrEnum):
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
    file_reference: str
    sha256: str
    level: ReferenceLevel
    founder_approved: bool
    read_only: bool = False
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.level is ReferenceLevel.MASTER_REFERENCE and not (self.founder_approved and self.read_only):
            raise ValueError("master references must be Founder-approved and read-only")
        if self.level is ReferenceLevel.FOUNDER_APPROVED_REFERENCE and not self.founder_approved:
            raise ValueError("canonical references require Founder approval")


@dataclass(frozen=True)
class FaceProfile:
    visible_attributes: tuple[str, ...]
    reference_ids: tuple[str, ...]
    evaluation_data: dict[str, Any] = field(default_factory=dict)
    founder_feedback_ids: tuple[str, ...] = ()


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
    texture: str = "natural, photorealistic, minimally retouched"


@dataclass(frozen=True)
class MakeupProfile:
    default: str = "natural, clean skin, defined lashes, natural brows, soft natural lips"


@dataclass(frozen=True)
class BodyProfile:
    attributes: tuple[str, ...] = ()
    calibrated: bool = False


@dataclass(frozen=True)
class BrandProfile:
    directions: tuple[str, ...] = ("photorealistic", "modern", "clean", "premium", "natural", "approachable", "minimalistic")
    palette: tuple[str, ...] = ("white", "neutral gray", "soft black", "soft violet", "controlled burgundy")
    realism_policy: str = "believable near-present photography, not fantasy, CGI, or cyberpunk"


@dataclass(frozen=True)
class IdentityLock:
    canonical_reference_ids: tuple[str, ...]
    face_constraints: tuple[str, ...]
    eye_constraints: tuple[str, ...] = ("blue eyes", "preserve shape")
    hair_constraints: tuple[str, ...] = ("light blonde family", "preserve hairline")
    skin_constraints: tuple[str, ...] = ("light", "natural texture", "no plastic smoothing")
    age_consistency: str = "stable young adult appearance"
    body_constraints: tuple[str, ...] = ()
    identity_strength_policy: str = "maximum for canonical AIRA output"

    def __post_init__(self) -> None:
        if not self.canonical_reference_ids:
            raise ValueError("identity lock requires a canonical reference")


@dataclass(frozen=True)
class VisualIdentityProfile:
    identity_id: str
    character_id: str
    name: str
    version: str
    status: IdentityStatus
    founder_approved: bool
    master_reference_id: str
    reference_ids: tuple[str, ...]
    face: FaceProfile
    hair: HairProfile = field(default_factory=HairProfile)
    eyes: EyeProfile = field(default_factory=EyeProfile)
    skin: SkinProfile = field(default_factory=SkinProfile)
    body: BodyProfile = field(default_factory=BodyProfile)
    makeup: MakeupProfile = field(default_factory=MakeupProfile)
    brand: BrandProfile = field(default_factory=BrandProfile)
    wardrobe_rules: tuple[str, ...] = ("prefer white shirt", "minimal jewelry", "controlled neutral families")
    allowed_variation: tuple[str, ...] = ("scene", "clothes", "pose", "expression", "lighting", "camera", "controlled hairstyle")
    forbidden_variation: tuple[str, ...] = ("face identity", "eye color", "major hair color", "age drift", "plastic skin")
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    history: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status in {IdentityStatus.APPROVED, IdentityStatus.ACTIVE} and not self.founder_approved:
            raise ValueError("approved/active identity requires Founder approval")
        if self.master_reference_id not in self.reference_ids:
            raise ValueError("master reference must be in reference set")


@dataclass(frozen=True)
class Wardrobe:
    category: str
    color: str
    material: str = "unspecified"
    fit: str = "clean relaxed"
    accessories: tuple[str, ...] = ()
    footwear: str | None = None
    brand_compatible: bool = True
    identity_compatible: bool = True


@dataclass(frozen=True)
class Camera:
    shot_type: str
    angle: str
    lens_equivalent: str
    camera_height: str
    orientation: str
    depth_of_field: str
    distance: str
    motion: str
    aspect_ratio: str


@dataclass(frozen=True)
class ProviderPolicy:
    required_capabilities: frozenset[str]
    allowed_provider_ids: frozenset[str] = frozenset()
    privacy_level: str = "canonical-reference-sensitive"


@dataclass(frozen=True)
class VisualGenerationRequest:
    request_id: str
    character_id: str
    identity_version: str
    purpose: str
    platform: str
    scene: str
    wardrobe: Wardrobe
    pose: str
    expression: Expression
    camera: Camera
    lighting: str
    aspect_ratio: str
    reference_ids: tuple[str, ...]
    task_profile: str
    provider_policy: ProviderPolicy
    candidate_count: int
    cost_limit: float
    founder_approval_required: bool = True

    def __post_init__(self) -> None:
        if self.aspect_ratio not in {"9:16", "4:5", "1:1", "16:9"}:
            raise ValueError("unsupported aspect ratio")
        if not 1 <= self.candidate_count <= 16 or self.cost_limit < 0:
            raise ValueError("invalid candidate count or cost limit")
        if not self.reference_ids:
            raise ValueError("AIRA generation requires identity references")


@dataclass(frozen=True)
class MediaDisclosure:
    generated_by_ai: bool = True
    edited_by_ai: bool = False
    provider: str = ""
    model: str = ""
    human_reviewed: bool = False
    founder_approved: bool = False
    platform_disclosure_required: bool = False
    disclosure_applied: bool = False


@dataclass(frozen=True)
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
    wardrobe: Wardrobe
    pose: str
    expression: Expression
    camera: Camera
    lighting: str
    file_reference: str
    sha256: str
    parent_asset_id: str | None = None
    edit_operation: str | None = None
    identity_score: float | None = None
    quality_score: float | None = None
    guardian_status: str = "PENDING"
    founder_status: str = "PENDING"
    usage_rights_metadata: dict[str, str] = field(default_factory=dict)
    disclosure: MediaDisclosure = field(default_factory=MediaDisclosure)
    status: AssetStatus = AssetStatus.GENERATED
    created_at: datetime = field(default_factory=utcnow)

    def edited_copy(self, file_reference: str, sha256: str, operation: str) -> "VisualAsset":
        return replace(self, asset_id=str(uuid4()), parent_asset_id=self.asset_id,
                       edit_operation=operation, file_reference=file_reference, sha256=sha256,
                       status=AssetStatus.GENERATED, created_at=utcnow())


@dataclass(frozen=True)
class VisualFeedback:
    feedback_id: str
    target_asset_id: str
    category: str
    severity: str
    reason: str
    founder_id: str
    created_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True)
class EvaluationResult:
    identity_score: float
    quality_score: float
    identity_reasons: tuple[str, ...] = ()
    quality_defects: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.identity_score <= 100 or not 0 <= self.quality_score <= 100:
            raise ValueError("scores must be from 0 to 100")
