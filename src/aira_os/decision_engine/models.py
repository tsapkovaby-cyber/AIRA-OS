"""Core Decision Engine data models.

These models intentionally contain no AI inference or autonomous execution logic.
They define the auditable architecture used to evaluate, explain, approve, and
store decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class DecisionType(str, Enum):
    """Supported categories of decisions."""

    OPERATIONAL = "operational"
    RESEARCH = "research"
    EDUCATIONAL = "educational"
    PUBLISHING = "publishing"
    STRATEGIC = "strategic"
    BUSINESS = "business"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    LEARNING = "learning"
    CONVERSATION = "conversation"


class DecisionStatus(str, Enum):
    """Lifecycle status for a decision."""

    DRAFT = "draft"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXECUTED = "executed"
    ARCHIVED = "archived"


class ApprovalStatus(str, Enum):
    """Approval state for founder-controlled decisions."""

    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    APPROVED = "approved"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    """Risk classification used by the approval workflow."""

    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceBand(str, Enum):
    """Human-readable confidence ranges."""

    VERIFIED = "verified"
    HIGHLY_RELIABLE = "highly_reliable"
    RELIABLE = "reliable"
    NEEDS_VERIFICATION = "needs_verification"
    DO_NOT_RECOMMEND = "do_not_recommend"


@dataclass(frozen=True)
class Alternative:
    """A possible option considered before selecting a decision."""

    name: str
    pros: list[str]
    cons: list[str]
    cost: str
    complexity: str
    expected_result: str
    risk: RiskLevel
    confidence: float
    recommendation: str


@dataclass(frozen=True)
class HistoryEvent:
    """Immutable audit event attached to a decision."""

    timestamp: datetime
    action: str
    actor: str
    details: str


@dataclass
class Decision:
    """Auditable decision object.

    The object keeps all evidence, alternatives, reasoning, approval state, and
    history needed to reproduce and explain the decision later.
    """

    type: DecisionType
    goal: str
    context: dict[str, Any]
    inputs: dict[str, Any]
    alternatives: list[Alternative]
    selected_option: Alternative
    confidence: float
    risk: RiskLevel
    reasoning: str
    constitution_checks: list[str]
    id: str = field(default_factory=lambda: f"decision-{uuid4()}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    required_approval: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    execution_status: DecisionStatus = DecisionStatus.DRAFT
    history: list[HistoryEvent] = field(default_factory=list)

    def record(self, action: str, actor: str, details: str) -> None:
        """Append an audit event without removing previous history."""

        self.history.append(
            HistoryEvent(
                timestamp=datetime.now(timezone.utc),
                action=action,
                actor=actor,
                details=details,
            )
        )
