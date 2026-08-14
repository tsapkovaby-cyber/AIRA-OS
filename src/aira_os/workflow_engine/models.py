"""Architecture-only workflow models.

The sprint scope explicitly excludes real execution, message queues, external APIs,
and orchestration runtimes. These models define the controlled workflow contract
that future agents and infrastructure will implement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    RESUMED = "resumed"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class StageStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    WAITING_FOUNDER = "waiting_founder"
    WAITING_GUARDIAN = "waiting_guardian"
    COMPLETED = "completed"


ExecutionState = StageStatus


class WorkflowType(StrEnum):
    RESEARCH = "research_workflow"
    KNOWLEDGE_UPDATE = "knowledge_update"
    CONTENT_CREATION = "content_creation"
    PUBLISHING = "publishing"
    DEVELOPMENT = "development"
    MAINTENANCE = "maintenance"
    LEARNING = "learning"
    MARKETING = "marketing"
    BUSINESS = "business"
    AUTOMATION = "automation"
    MONITORING = "monitoring"


class ExecutionPolicy(StrEnum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"


class ApprovalGate(StrEnum):
    BEFORE_PUBLICATION = "before_publication"
    BEFORE_BRAND_CHANGES = "before_brand_changes"
    BEFORE_BUSINESS_DECISIONS = "before_business_decisions"
    BEFORE_ARCHITECTURE_CHANGES = "before_architecture_changes"
    BEFORE_EXTERNAL_ACTIONS = "before_external_actions"


class BackoffStrategy(StrEnum):
    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    MANUAL = "manual"


@dataclass(frozen=True)
class RetryPolicy:
    maximum_attempts: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    automatic_retry: bool = True
    escalation_required: bool = True

    def __post_init__(self) -> None:
        if self.maximum_attempts < 1:
            raise ValueError("maximum_attempts must be at least 1")


@dataclass
class ConstitutionCheck:
    transparency_present: bool = True
    evidence_sufficient: bool = True
    approval_present: bool = True
    risk_acceptable: bool = True
    constitution_violated: bool = False
    reason: str = "Constitution requirements satisfied."

    @property
    def can_continue(self) -> bool:
        return all(
            [
                not self.constitution_violated,
                self.transparency_present,
                self.evidence_sufficient,
                self.approval_present,
                self.risk_acceptable,
            ]
        )


@dataclass
class ExecutionHistoryEntry:
    agent: str
    action: str
    result: str
    reason: str
    approval: str | None = None
    logs: list[str] = field(default_factory=list)
    version: str = "S008-1.0"
    timestamp: datetime = field(default_factory=utc_now)


@dataclass
class Incident:
    workflow_id: str
    cause: str
    impact: str
    responsible_agent: str
    resolution: str = "pending"
    lessons_learned: str = "pending"
    timeline: list[ExecutionHistoryEntry] = field(default_factory=list)
    incident_id: str = field(default_factory=lambda: f"incident-{uuid4()}")
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class Stage:
    title: str
    description: str
    required_agent: str
    dependencies: list[str] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: int | None = None
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    status: StageStatus = StageStatus.PENDING
    retry_count: int = 0
    stage_id: str = field(default_factory=lambda: f"stage-{uuid4()}")

    def validate(self, known_stage_ids: set[str]) -> None:
        missing = set(self.dependencies) - known_stage_ids
        if missing:
            raise ValueError(f"Unknown stage dependencies: {sorted(missing)}")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive when provided")

    @property
    def can_retry(self) -> bool:
        return self.retry_count + 1 < self.retry_policy.maximum_attempts


@dataclass
class WorkflowMetrics:
    duration_seconds: float = 0
    execution_success_rate: float = 0
    average_retry_count: float = 0
    average_approval_time_seconds: float = 0
    failure_rate: float = 0
    incident_count: int = 0
    workflow_efficiency: float = 0
    agent_reliability: dict[str, float] = field(default_factory=dict)


@dataclass
class Workflow:
    goal: str
    description: str
    owner: str
    stages: list[Stage]
    workflow_type: WorkflowType
    execution_policy: ExecutionPolicy = ExecutionPolicy.SEQUENTIAL
    priority: str = "normal"
    dependencies: list[str] = field(default_factory=list)
    assigned_agents: dict[str, str] = field(default_factory=dict)
    approval_gates: list[ApprovalGate] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    execution_history: list[ExecutionHistoryEntry] = field(default_factory=list)
    metrics: WorkflowMetrics = field(default_factory=WorkflowMetrics)
    incidents: list[Incident] = field(default_factory=list)
    workflow_id: str = field(default_factory=lambda: f"workflow-{uuid4()}")
    created_date: datetime = field(default_factory=utc_now)
    updated_date: datetime = field(default_factory=utc_now)

    def validate(self) -> None:
        if not self.stages:
            raise ValueError("workflow must contain at least one stage")
        stage_ids = {stage.stage_id for stage in self.stages}
        if len(stage_ids) != len(self.stages):
            raise ValueError("stage IDs must be unique")
        for stage in self.stages:
            stage.validate(stage_ids)

    def record(self, entry: ExecutionHistoryEntry) -> None:
        self.execution_history.append(entry)
        self.updated_date = utc_now()
