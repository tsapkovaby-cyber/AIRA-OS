"""Provider-neutral perception domain models with immutable source lineage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Mapping, Sequence
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def now() -> datetime:
    return datetime.now(UTC)


class MediaType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    SCREENSHOT = "SCREENSHOT"
    AUDIO = "AUDIO"
    VOICE_MESSAGE = "VOICE_MESSAGE"
    VIDEO = "VIDEO"
    PDF = "PDF"
    DOCUMENT = "DOCUMENT"
    WEB_CAPTURE = "WEB_CAPTURE"
    TOOL_OUTPUT = "TOOL_OUTPUT"
    MULTIMODAL_BUNDLE = "MULTIMODAL_BUNDLE"


class PrivacyLevel(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PRIVATE = "PRIVATE"
    RESTRICTED = "RESTRICTED"


class Confidence(str, Enum):
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    MEDIUM_CONFIDENCE = "MEDIUM_CONFIDENCE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class AssetReference:
    asset_id: str
    uri: str
    media_type: MediaType
    checksum: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Observation:
    source_id: str
    type: str
    content: str
    location: str | None
    confidence: Confidence
    model: str
    observation_id: str = field(default_factory=lambda: new_id("obs"))
    created_at: datetime = field(default_factory=now)


@dataclass(frozen=True)
class TimelineEntry:
    start_seconds: float
    end_seconds: float
    content: str
    source_id: str
    confidence: Confidence = Confidence.MEDIUM_CONFIDENCE


@dataclass(frozen=True)
class PerceptionRequest:
    source: str
    user: str
    media_type: MediaType
    asset_references: tuple[AssetReference, ...] = ()
    purpose: str = "understand"
    context: Mapping[str, Any] = field(default_factory=dict)
    requested_analysis: tuple[str, ...] = ()
    model_policy: Mapping[str, Any] = field(default_factory=dict)
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL
    request_id: str = field(default_factory=lambda: new_id("preq"))
    created_at: datetime = field(default_factory=now)


@dataclass(frozen=True)
class PerceptionResult:
    request_id: str
    observations: tuple[Observation, ...]
    extracted_text: str = ""
    objects: tuple[str, ...] = ()
    scenes: tuple[str, ...] = ()
    speech_transcript: str = ""
    speakers: tuple[str, ...] = ()
    timeline: tuple[TimelineEntry, ...] = ()
    confidence: Confidence = Confidence.UNRESOLVED
    uncertainty: tuple[str, ...] = ()
    model: str = ""
    source_references: tuple[AssetReference, ...] = ()
    costs: Mapping[str, float] = field(default_factory=dict)
    result_id: str = field(default_factory=lambda: new_id("pres"))
    created_at: datetime = field(default_factory=now)


@dataclass(frozen=True)
class MultimodalBundle:
    assets: tuple[AssetReference, ...]
    relationships: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    text: str = ""
    bundle_id: str = field(default_factory=lambda: new_id("bundle"))

    def __post_init__(self) -> None:
        ids = {asset.asset_id for asset in self.assets}
        referenced = {item for values in self.relationships.values() for item in values}
        if not referenced.issubset(ids):
            raise ValueError("bundle relationships must reference contained assets")


@dataclass(frozen=True)
class ProviderOutput:
    observations: Sequence[Mapping[str, Any]] = ()
    extracted_text: str = ""
    objects: Sequence[str] = ()
    scenes: Sequence[str] = ()
    transcript: str = ""
    speakers: Sequence[str] = ()
    timeline: Sequence[TimelineEntry] = ()
    confidence: Confidence = Confidence.MEDIUM_CONFIDENCE
    uncertainty: Sequence[str] = ()
    cost: float = 0.0
