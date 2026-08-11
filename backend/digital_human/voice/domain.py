"""Immutable domain types for AIRA's voice identity.

No type in this module uploads audio. Provider adapters receive only an approved
provider profile, never an unrestricted master-reference path.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping

MASTER_REFERENCE_ID = "AIRA_MASTER_VOICE_REFERENCE_V1"
VOICE_IDENTITY_ID = "AIRA_VOICE_IDENTITY_V1"
VOICE_BENCHMARK_ID = "AIRA_VOICE_BENCHMARK_V1"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class VoiceIdentityStatus(StrEnum):
    DRAFT = "DRAFT"
    CALIBRATING = "CALIBRATING"
    FOUNDER_REVIEW = "FOUNDER_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class ReferenceLevel(StrEnum):
    MASTER = "MASTER_VOICE_REFERENCE"
    FOUNDER_APPROVED = "FOUNDER_APPROVED_VOICE_REFERENCE"
    TEST = "VOICE_TEST_REFERENCE"
    GENERATED = "GENERATED_SPEECH"


class Emotion(StrEnum):
    NEUTRAL = "NEUTRAL"
    FRIENDLY = "FRIENDLY"
    CURIOUS = "CURIOUS"
    EXPLANATORY = "EXPLANATORY"
    CONFIDENT = "CONFIDENT"
    EXCITED_SUBTLE = "EXCITED_SUBTLE"
    SERIOUS = "SERIOUS"
    THOUGHTFUL = "THOUGHTFUL"
    SOFT = "SOFT"
    AIRA_DEFAULT = "AIRA_DEFAULT"


class Pace(StrEnum):
    SLOW = "SLOW"
    NORMAL = "NORMAL"
    DYNAMIC = "DYNAMIC"
    SHORT_FORM = "SHORT_FORM"
    LONG_FORM = "LONG_FORM"


class ProviderStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    RESEARCHED = "RESEARCHED"
    RISK_REVIEWED = "RISK_REVIEWED"
    FOUNDER_APPROVED = "FOUNDER_APPROVED"
    TESTING = "TESTING"
    APPROVED = "APPROVED"
    DISABLED = "DISABLED"


class SpeechAssetStatus(StrEnum):
    GENERATED = "GENERATED"
    EVALUATING = "EVALUATING"
    REJECTED_IDENTITY = "REJECTED_IDENTITY"
    REJECTED_QUALITY = "REJECTED_QUALITY"
    GUARDIAN_REVIEW = "GUARDIAN_REVIEW"
    FOUNDER_REVIEW = "FOUNDER_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class ConsentMetadata:
    voice_source: str = "FOUNDER_PROVIDED"
    consent_status: str = "APPROVED_FOR_AIRA"
    permitted_character: str = "AIRA"
    automatic_third_party_sharing: bool = False
    provider_upload: str = "REQUIRES_POLICY_CHECK"

    def permits(self, character: str) -> bool:
        return character == self.permitted_character


@dataclass(frozen=True)
class VoiceReference:
    asset_id: str
    level: ReferenceLevel
    file_reference: str
    sha256: str
    parent_asset_id: str | None = None
    founder_approved: bool = False
    read_only: bool = True

    def derive(self, asset_id: str, file_reference: str, sha256: str) -> "VoiceReference":
        if self.level is ReferenceLevel.GENERATED:
            raise ValueError("Generated speech cannot become a canonical reference")
        return VoiceReference(asset_id, ReferenceLevel.TEST, file_reference, sha256, self.asset_id)


@dataclass(frozen=True)
class PronunciationEntry:
    term: str
    language: str
    written_form: str
    pronunciation_hint: str
    phoneme_form: str | None = None
    provider_overrides: Mapping[str, str] = field(default_factory=dict)
    status: str = "TESTING"
    founder_approved: bool = False


@dataclass(frozen=True)
class VoiceIdentityLock:
    master_reference_id: str
    approved_reference_ids: tuple[str, ...]
    voice_identity_version: str
    identity_threshold: float = 80.0
    founder_review_threshold: float = 70.0
    language_profiles: tuple[str, ...] = ("ru", "en")
    allowed_variation: tuple[str, ...] = ("pace", "emotion", "pauses", "intonation")
    forbidden_variation: tuple[str, ...] = ("speaker", "timbre", "material_pitch", "identity")
    compatible_providers: tuple[str, ...] = ()

    def decision(self, identity_score: float) -> SpeechAssetStatus:
        if not 0 <= identity_score <= 100:
            raise ValueError("Identity score must be between 0 and 100")
        if identity_score >= self.identity_threshold:
            return SpeechAssetStatus.APPROVED
        if identity_score >= self.founder_review_threshold:
            return SpeechAssetStatus.FOUNDER_REVIEW
        return SpeechAssetStatus.REJECTED_IDENTITY


@dataclass(frozen=True)
class VoiceIdentityProfile:
    voice_identity_id: str
    character_id: str
    version: str
    master_reference: VoiceReference
    approved_reference_ids: tuple[str, ...]
    voice_characteristics: Mapping[str, str]
    speech_styles: Mapping[str, Mapping[str, str]]
    language_profiles: Mapping[str, Mapping[str, str]]
    pronunciation_rules: tuple[PronunciationEntry, ...]
    emotion_profiles: tuple[Emotion, ...]
    pacing_rules: tuple[Pace, ...]
    provider_profile_ids: tuple[str, ...]
    safety_rules: tuple[str, ...]
    consent: ConsentMetadata
    founder_approved: bool
    status: VoiceIdentityStatus
    created_at: datetime
    updated_at: datetime
    history: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.master_reference.level is not ReferenceLevel.MASTER:
            raise ValueError("Master reference must have MASTER level")
        if not self.master_reference.read_only:
            raise ValueError("Master reference must be read-only")
        if not self.consent.permits(self.character_id):
            raise ValueError("Voice consent does not cover this character")
        if self.status is VoiceIdentityStatus.ACTIVE and not self.founder_approved:
            raise ValueError("Only Founder-approved identity can be active")

    def replace_master(self, _: VoiceReference) -> "VoiceIdentityProfile":
        raise PermissionError("DENIED: canonical master replacement requires explicit Founder workflow")


@dataclass(frozen=True)
class SpeechGenerationRequest:
    request_id: str
    character_id: str
    voice_identity_version: str
    text: str
    language: str
    speech_profile: str
    emotion: Emotion
    pace: Pace
    purpose: str
    platform: str
    pronunciation_rules: tuple[str, ...] = ()
    provider_policy: str = "APPROVED_ONLY"
    output_format: str = "wav"
    cost_limit: float = 0.0
    approval_requirement: str = "GUARDIAN"
    high_risk: bool = False
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.character_id != "AIRA" or not self.text.strip():
            raise ValueError("Speech requires non-empty approved AIRA text")
        if self.language not in {"ru", "en"}:
            raise ValueError("Unsupported language")
        if self.cost_limit < 0:
            raise ValueError("Cost limit cannot be negative")
        if self.high_risk and self.approval_requirement != "FOUNDER":
            raise ValueError("High-risk speech requires Founder approval")


@dataclass(frozen=True)
class ProviderVoiceProfile:
    profile_id: str
    provider: str
    external_voice_id: str
    source_reference_version: str
    status: ProviderStatus
    consent_scope: str
    deletion_support: bool
    created_at: datetime = field(default_factory=utcnow)
    last_verified: datetime = field(default_factory=utcnow)


@dataclass(frozen=True)
class SpeechAsset:
    asset_id: str
    character_id: str
    voice_identity_version: str
    speech_request_id: str
    provider: str
    provider_voice_profile_id: str
    text_version: str
    language: str
    emotion: Emotion
    pace: Pace
    pronunciation_version: str
    identity_score: float | None
    quality_score: float | None
    founder_status: str
    guardian_status: str
    file_reference: str
    sha256: str
    parent_asset_id: str
    status: SpeechAssetStatus = SpeechAssetStatus.GENERATED
    generated_speech: bool = True
    voice_source: str = "FOUNDER_DERIVED"
    speaker_character: str = "AIRA"
    created_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not self.parent_asset_id:
            raise ValueError("Speech assets must preserve lineage")
        if not self.generated_speech or self.speaker_character != "AIRA":
            raise ValueError("Generated AIRA speech must not represent authentic Founder speech")

    def with_status(self, status: SpeechAssetStatus) -> "SpeechAsset":
        return replace(self, status=status)


@dataclass(frozen=True)
class VoiceFeedback:
    asset_id: str
    category: str
    severity: str
    provider: str
    profile: str
    result: str
    comment: str
    created_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True)
class Budget:
    per_request: float
    daily: float
    monthly: float
    experiment: float

    def authorize(self, estimated_cost: float, spent_today: float, spent_month: float, experiment: bool = False) -> bool:
        cap = self.experiment if experiment else self.per_request
        return estimated_cost <= cap and spent_today + estimated_cost <= self.daily and spent_month + estimated_cost <= self.monthly
