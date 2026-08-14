"""Core Guardian Engine data models.

These models intentionally describe architecture and policy state only. They do
not perform AI moderation, legal automation, censorship, or integrations with
external compliance services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable
from uuid import uuid4


class ReviewResult(str, Enum):
    """Canonical Guardian review outcomes."""

    APPROVED = "Approved"
    APPROVED_WITH_NOTES = "Approved with Notes"
    NEEDS_REVISION = "Needs Revision"
    REJECTED = "Rejected"
    ESCALATED = "Escalated"
    BLOCKED = "Blocked"


class ApprovalStatus(str, Enum):
    """Founder or delegated approval state."""

    NOT_REQUIRED = "Not Required"
    PENDING_FOUNDER = "Pending Founder Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class RiskLevel(str, Enum):
    """Risk severity levels used by architecture-only classifiers."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskCategory(str, Enum):
    """Risk domains monitored by Guardian."""

    TECHNICAL = "Technical"
    LEGAL = "Legal"
    BUSINESS = "Business"
    BRAND = "Brand"
    EDUCATIONAL = "Educational"
    SECURITY = "Security"
    OPERATIONAL = "Operational"
    REPUTATION = "Reputation"


class ClaimType(str, Enum):
    """Transparency labels required for public claims."""

    FACT = "Fact"
    OPINION = "Opinion"
    ASSUMPTION = "Assumption"
    PREDICTION = "Prediction"


@dataclass(frozen=True)
class EvidenceRecord:
    """Evidence required for each important public claim."""

    claim: str
    claim_type: ClaimType
    primary_source: str | None
    secondary_source: str | None
    publication_date: str | None
    confidence: float
    verification_status: str
    supporting_references: tuple[str, ...] = ()

    def has_required_sources(self) -> bool:
        """Return whether the evidence satisfies Guardian publication rules."""

        return bool(self.primary_source and self.secondary_source)


@dataclass(frozen=True)
class ValidationIssue:
    """A policy, evidence, risk, or transparency issue found in a review."""

    category: str
    message: str
    severity: RiskLevel = RiskLevel.MEDIUM
    recommendation: str | None = None


@dataclass
class Review:
    """Guardian review object for workflows, content, and public actions."""

    workflow: str
    reviewer: str
    review_type: str
    result: ReviewResult
    confidence: float
    risk: RiskLevel
    issues: list[ValidationIssue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    history: list[str] = field(default_factory=list)
    evidence: list[EvidenceRecord] = field(default_factory=list)
    review_id: str = field(default_factory=lambda: f"grv-{uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_history(self, event: str) -> None:
        """Append an auditable timeline entry."""

        self.history.append(f"{datetime.now(timezone.utc).isoformat()} — {event}")

    @property
    def is_blocking(self) -> bool:
        """Return whether this review prevents workflow execution."""

        return self.result in {ReviewResult.REJECTED, ReviewResult.BLOCKED, ReviewResult.ESCALATED}


@dataclass
class Incident:
    """Incident created when Guardian blocks execution."""

    review_id: str
    reason: str
    risk: RiskLevel
    notify_founder: bool = True
    suggested_resolution: str | None = None
    history: list[str] = field(default_factory=list)
    incident_id: str = field(default_factory=lambda: f"gic-{uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_history(self, event: str) -> None:
        """Append an auditable incident timeline entry."""

        self.history.append(f"{datetime.now(timezone.utc).isoformat()} — {event}")


def highest_risk(issues: Iterable[ValidationIssue]) -> RiskLevel:
    """Return the highest severity in a collection of issues."""

    order = {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 1,
        RiskLevel.HIGH: 2,
        RiskLevel.CRITICAL: 3,
    }
    return max((issue.severity for issue in issues), key=lambda item: order[item], default=RiskLevel.LOW)
