"""Architecture models for the AIRA Research Engine.

The Research Engine collects, classifies, verifies, normalizes, and forwards
research candidates. It does not scrape, publish, schedule work, or make final
knowledge conclusions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import Enum
from statistics import mean
from typing import Protocol
from uuid import uuid4


class SourceCategory(str, Enum):
    OFFICIAL = "official"
    ACADEMIC = "academic"
    DEVELOPER = "developer"
    INDUSTRY = "industry"
    COMMUNITY = "community"
    EXPERIMENTAL = "experimental"
    INTERNAL = "internal"


class TrustLevel(str, Enum):
    LEVEL_A = "level_a"
    LEVEL_B = "level_b"
    LEVEL_C = "level_c"
    LEVEL_D = "level_d"


class InformationCategory(str, Enum):
    AI_MODELS = "ai_models"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    VOICE = "voice"
    AUTOMATION = "automation"
    CODING = "coding"
    ROBOTICS = "robotics"
    HARDWARE = "hardware"
    BUSINESS = "business"
    PRICING = "pricing"
    OPEN_SOURCE = "open_source"
    SECURITY = "security"
    RESEARCH = "research"
    BENCHMARKS = "benchmarks"
    API = "api"
    AGENTS = "agents"


class Freshness(str, Enum):
    FRESH = "fresh"
    RECENT = "recent"
    CURRENT = "current"
    OLD = "old"
    HISTORICAL = "historical"
    ARCHIVED = "archived"


class PipelineStage(str, Enum):
    DISCOVERY = "discovery"
    COLLECTION = "collection"
    CLASSIFICATION = "classification"
    SOURCE_VERIFICATION = "source_verification"
    DUPLICATE_DETECTION = "duplicate_detection"
    NORMALIZATION = "normalization"
    CONFIDENCE_EVALUATION = "confidence_evaluation"
    KNOWLEDGE_CANDIDATE = "knowledge_candidate"
    KNOWLEDGE_ENGINE = "knowledge_engine"


class OutputType(str, Enum):
    DAILY_REPORT = "daily_report"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_TRENDS = "monthly_trends"
    RELEASE_ALERT = "release_alert"
    CRITICAL_UPDATE = "critical_update"
    RESEARCH_CANDIDATE = "research_candidate"


TRUST_BY_SOURCE_CATEGORY: dict[SourceCategory, TrustLevel] = {
    SourceCategory.OFFICIAL: TrustLevel.LEVEL_A,
    SourceCategory.ACADEMIC: TrustLevel.LEVEL_A,
    SourceCategory.DEVELOPER: TrustLevel.LEVEL_B,
    SourceCategory.INDUSTRY: TrustLevel.LEVEL_B,
    SourceCategory.COMMUNITY: TrustLevel.LEVEL_C,
    SourceCategory.EXPERIMENTAL: TrustLevel.LEVEL_C,
    SourceCategory.INTERNAL: TrustLevel.LEVEL_B,
}


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    category: SourceCategory
    trust_level: TrustLevel | None = None
    verified: bool = False

    def effective_trust_level(self) -> TrustLevel:
        return self.trust_level or TRUST_BY_SOURCE_CATEGORY[self.category]


@dataclass(frozen=True)
class Reference:
    source_name: str
    url: str
    title: str | None = None
    accessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class ResearchScore:
    source_quality: float
    evidence_quality: float
    practical_importance: float
    business_impact: float
    educational_value: float
    novelty: float
    confidence: float

    def __post_init__(self) -> None:
        for field_name, value in self.__dict__.items():
            if not 0 <= value <= 1:
                raise ValueError(f"{field_name} must be between 0 and 1")

    @property
    def overall(self) -> float:
        return mean(self.__dict__.values())


@dataclass(frozen=True)
class SecurityContext:
    owner: str
    visibility: str
    permissions: tuple[str, ...] = ()


@dataclass
class ResearchItem:
    title: str
    summary: str
    source: Source
    author: str | None
    publication_date: date | None
    language: str
    category: InformationCategory
    tags: set[str]
    security: SecurityContext
    item_id: str = field(default_factory=lambda: f"research_{uuid4().hex}")
    discovery_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    trust_level: TrustLevel | None = None
    confidence: float = 0.0
    references: list[Reference] = field(default_factory=list)
    freshness: Freshness = Freshness.CURRENT
    score: ResearchScore | None = None
    duplicate_of: str | None = None
    duplicate_links: set[str] = field(default_factory=set)
    conflicts: set[str] = field(default_factory=set)
    history: list[str] = field(default_factory=list)
    archived: bool = False

    def __post_init__(self) -> None:
        self.trust_level = self.trust_level or self.source.effective_trust_level()
        self.tags = {tag.strip().lower() for tag in self.tags if tag.strip()}
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class KnowledgeCandidate:
    research_item: ResearchItem
    pipeline_stage: PipelineStage = PipelineStage.KNOWLEDGE_CANDIDATE
    output_type: OutputType = OutputType.RESEARCH_CANDIDATE


class PipelineStep(Protocol):
    """Interface for architecture-only pipeline steps."""

    stage: PipelineStage

    def run(self, item: ResearchItem) -> ResearchItem:
        """Transform or annotate a research item without publishing it."""
