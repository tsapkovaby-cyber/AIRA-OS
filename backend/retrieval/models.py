"""Domain contracts for retrieval. All scores are normalized to ``[0, 1]``."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Domain(StrEnum):
    PROJECT = "PROJECT"; AI_TOOLS = "AI_TOOLS"; RESEARCH = "RESEARCH"
    MEMORY = "MEMORY"; CONTENT = "CONTENT"; DECISIONS = "DECISIONS"
    BRAND = "BRAND"; AGENTS = "AGENTS"; WORKFLOWS = "WORKFLOWS"
    FOUNDER_PRIVATE = "FOUNDER_PRIVATE"; PUBLIC_KNOWLEDGE = "PUBLIC_KNOWLEDGE"


class Mode(StrEnum):
    KEYWORD = "KEYWORD"; SEMANTIC = "SEMANTIC"; GRAPH = "GRAPH"; HYBRID = "HYBRID"
    TIME_AWARE = "TIME_AWARE"; SOURCE_AWARE = "SOURCE_AWARE"
    MEMORY_AWARE = "MEMORY_AWARE"; EXACT_ID = "EXACT_ID"


class SecurityScope(StrEnum):
    PUBLIC = "PUBLIC"; INTERNAL = "INTERNAL"; FOUNDER_PRIVATE = "FOUNDER_PRIVATE"
    SYSTEM_SECRET = "SYSTEM_SECRET"


class FreshnessStatus(StrEnum):
    CURRENT = "CURRENT"; STALE = "STALE"; HISTORICAL = "HISTORICAL"
    DEPRECATED = "DEPRECATED"; UNVERIFIED = "UNVERIFIED"


class MissingStatus(StrEnum):
    INSUFFICIENT_KNOWLEDGE = "INSUFFICIENT_KNOWLEDGE"


@dataclass(slots=True)
class TimeRange:
    after: datetime | None = None
    before: datetime | None = None


@dataclass(slots=True)
class RetrievalQuery:
    raw_query: str
    requester: str
    agent_id: str | None = None
    task_id: str | None = None
    workflow_id: str | None = None
    normalized_query: str = ""
    intent: str = "lookup"
    domains: set[Domain] = field(default_factory=set)
    memory_scope: str = "approved"
    security_scope: SecurityScope = SecurityScope.INTERNAL
    time_range: TimeRange | None = None
    freshness_requirement: FreshnessStatus | None = None
    result_limit: int = 10
    query_id: str = field(default_factory=lambda: f"Q-{uuid4().hex}")
    created_at: datetime = field(default_factory=utcnow)
    task_permissions: set[SecurityScope] = field(default_factory=set)


@dataclass(slots=True)
class EvidenceReference:
    source_id: str
    locator: str | None = None


@dataclass(slots=True)
class RetrievalResult:
    result_id: str
    source_type: str
    source_id: str
    title: str
    summary: str
    relevant_passage: str
    domain: Domain
    security_classification: SecurityScope = SecurityScope.INTERNAL
    score: float = 0.0
    keyword_score: float = 0.0
    semantic_score: float = 0.0
    graph_score: float = 0.0
    confidence: float = 1.0
    freshness: float = 1.0
    freshness_status: FreshnessStatus = FreshnessStatus.CURRENT
    importance: float = .5
    source_trust: float = .5
    relationships: list[str] = field(default_factory=list)
    version: str = "1"
    evidence_references: list[EvidenceReference] = field(default_factory=list)
    last_verified: datetime | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Conflict:
    claim_a: str; evidence_a: list[str]; claim_b: str; evidence_b: list[str]
    confidence: float; dates: list[datetime] = field(default_factory=list)
    resolution_status: str = "UNRESOLVED"


@dataclass(slots=True)
class RetrievalTrace:
    searched_stores: list[str] = field(default_factory=list)
    modes: list[Mode] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    candidates_found: int = 0
    selected_reasons: dict[str, str] = field(default_factory=dict)
    excluded: dict[str, str] = field(default_factory=dict)
    conflicts_detected: int = 0
    cache_hit: bool = False


@dataclass(slots=True)
class RetrievalPackage:
    query: RetrievalQuery
    intent: str
    selected_sources: list[RetrievalResult]
    evidence_summary: str
    confidence: float
    conflicts: list[Conflict]
    missing_information: MissingStatus | None
    suggested_next_action: str | None
    context: str
    context_tokens_estimate: int
    trace: RetrievalTrace


@dataclass(slots=True)
class SearchPlan:
    stores: list[str]; modes: list[Mode]; candidate_limit: int
    graph_depth: int = 0


@dataclass(slots=True)
class Chunk:
    chunk_id: str; document_id: str; version: str; section: str; text: str
    start_offset: int; end_offset: int; hash: str
    metadata: dict[str, Any] = field(default_factory=dict)
    security_scope: SecurityScope = SecurityScope.INTERNAL
    embedding_status: str = "PENDING"


@dataclass(slots=True)
class VectorRecord:
    vector_id: str; source_type: str; source_id: str; chunk_id: str
    embedding_version: str; text_hash: str; vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
