from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Mapping
from uuid import uuid4

from .enums import ClaimKind, ContentStatus, ReviewStatus
from .errors import ContentError, EvidenceError


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SourceReference:
    source_id: str
    uri: str
    title: str

    def __post_init__(self) -> None:
        if not all((self.source_id.strip(), self.uri.strip(), self.title.strip())):
            raise ContentError("source id, URI, and title are required")


@dataclass(frozen=True)
class EvidenceClaim:
    claim_id: str
    text: str
    kind: ClaimKind
    source_ids: tuple[str, ...] = ()
    research_ids: tuple[str, ...] = ()
    knowledge_ids: tuple[str, ...] = ()
    experiment_id: str | None = None

    def validate(self, known_source_ids: set[str]) -> None:
        if self.kind in {ClaimKind.FACT, ClaimKind.TEST_RESULT} and not self.source_ids:
            raise EvidenceError(f"{self.kind} claim requires a source")
        if not set(self.source_ids) <= known_source_ids:
            raise EvidenceError("claim refers to an unknown source")
        if self.kind is ClaimKind.TEST_RESULT and not self.experiment_id:
            raise EvidenceError("test-result claim requires a recorded experiment")


@dataclass(frozen=True)
class ContentBrief:
    topic: str
    why_now: str
    audience: str
    problem: str
    main_insight: str
    evidence: tuple[EvidenceClaim, ...]
    content_goal: str
    platform: str
    format: str
    tone: str
    cta: str
    sources: tuple[SourceReference, ...]
    risks: tuple[str, ...] = ()
    required_disclaimer: str | None = None

    def validate(self) -> None:
        required = (self.topic, self.why_now, self.audience, self.problem, self.main_insight,
                    self.content_goal, self.platform, self.format, self.tone, self.cta)
        if any(not value.strip() for value in required):
            raise ContentError("all required brief fields must be non-empty")
        ids = {source.source_id for source in self.sources}
        if len(ids) != len(self.sources):
            raise ContentError("source IDs must be unique")
        for claim in self.evidence:
            claim.validate(ids)


@dataclass(frozen=True)
class ContentRequest:
    topic: str
    goal: str
    audience: str
    platform: str
    content_type: str
    authoring_agent: str
    language: str = "ru"
    workflow_id: str | None = None
    campaign_id: str | None = None


@dataclass(frozen=True)
class RevisionRequest:
    reason: str
    requested_changes: tuple[str, ...]
    reviewer: str
    timestamp: datetime = field(default_factory=utcnow)
    priority: str = "NORMAL"
    original_version: int = 1
    new_version: int = 2

    def __post_init__(self) -> None:
        if not self.reason.strip() or not self.reviewer.strip() or not self.requested_changes:
            raise ContentError("revision reason, changes, and reviewer are required")
        if self.new_version != self.original_version + 1:
            raise ContentError("revision must create the next version")


@dataclass(frozen=True)
class Content:
    content_id: str
    title: str
    content_type: str
    topic: str
    goal: str
    target_audience: str
    target_platform: str
    language: str
    status: ContentStatus
    created_at: datetime
    updated_at: datetime
    authoring_agent: str
    research_references: tuple[str, ...]
    knowledge_references: tuple[str, ...]
    source_references: tuple[SourceReference, ...]
    confidence: float
    content_body: str
    call_to_action: str
    disclaimer: str | None
    guardian_status: ReviewStatus
    founder_approval_status: ReviewStatus
    version: int
    parent_content_id: str | None = None
    campaign_id: str | None = None
    analytics_id: str | None = None
    claims: tuple[EvidenceClaim, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def draft(cls, request: ContentRequest, brief: ContentBrief, body: str, confidence: float) -> Content:
        now = utcnow()
        item = cls(
            content_id=f"CONTENT-{uuid4().hex[:12].upper()}", title=brief.main_insight,
            content_type=request.content_type, topic=request.topic, goal=request.goal,
            target_audience=request.audience, target_platform=request.platform,
            language=request.language, status=ContentStatus.DRAFT, created_at=now, updated_at=now,
            authoring_agent=request.authoring_agent,
            research_references=tuple(dict.fromkeys(i for c in brief.evidence for i in c.research_ids)),
            knowledge_references=tuple(dict.fromkeys(i for c in brief.evidence for i in c.knowledge_ids)),
            source_references=brief.sources, confidence=confidence, content_body=body,
            call_to_action=brief.cta, disclaimer=brief.required_disclaimer,
            guardian_status=ReviewStatus.NOT_REQUESTED,
            founder_approval_status=ReviewStatus.NOT_REQUESTED, version=1,
            campaign_id=request.campaign_id, claims=brief.evidence,
            metadata={"visibility": "private", "workflow_id": request.workflow_id or ""},
        )
        item.validate()
        return item

    def validate(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ContentError("confidence must be between zero and one")
        if self.version < 1 or not self.content_body.strip():
            raise ContentError("content body and positive version are required")
        ids = {source.source_id for source in self.source_references}
        for claim in self.claims:
            claim.validate(ids)
        if self.status is ContentStatus.READY_TO_PUBLISH and not (
            self.guardian_status is ReviewStatus.APPROVED
            and self.founder_approval_status is ReviewStatus.APPROVED
        ):
            raise ContentError("ready content requires Guardian and Founder approval")
        if self.status is ContentStatus.PUBLISHED:
            raise ContentError("Content Engine cannot mark content as published")

    def next_version(self, *, body: str, revision: RevisionRequest) -> Content:
        if revision.original_version != self.version:
            raise ContentError("revision does not target the current version")
        result = replace(self, content_body=body, version=revision.new_version,
                         updated_at=utcnow(), status=ContentStatus.DRAFT,
                         guardian_status=ReviewStatus.NOT_REQUESTED,
                         founder_approval_status=ReviewStatus.NOT_REQUESTED)
        result.validate()
        return result
