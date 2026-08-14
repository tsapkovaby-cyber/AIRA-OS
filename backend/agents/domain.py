"""Domain contracts for registered AIRA workers.

The objects in this module contain configuration, never provider credentials.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import Any, Mapping, Protocol
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AgentType(str, Enum):
    RESEARCH = "RESEARCH"
    KNOWLEDGE = "KNOWLEDGE"
    MEMORY = "MEMORY"
    CONTENT = "CONTENT"
    GUARDIAN = "GUARDIAN"
    ANALYTICS = "ANALYTICS"
    BUSINESS = "BUSINESS"
    PUBLISHING = "PUBLISHING"
    CEO_ASSISTANT = "CEO_ASSISTANT"


class AgentStatus(str, Enum):
    REGISTERED = "REGISTERED"
    INACTIVE = "INACTIVE"
    READY = "READY"
    BUSY = "BUSY"
    PAUSED = "PAUSED"
    DEGRADED = "DEGRADED"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    RETIRED = "RETIRED"


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class Capability(str, Enum):
    RESEARCH = "RESEARCH"
    SUMMARIZE = "SUMMARIZE"
    CLASSIFY = "CLASSIFY"
    COMPARE = "COMPARE"
    GENERATE_DRAFT = "GENERATE_DRAFT"
    REVIEW_CONTENT = "REVIEW_CONTENT"
    ANALYZE_METRICS = "ANALYZE_METRICS"
    PUBLISH_APPROVED_CONTENT = "PUBLISH_APPROVED_CONTENT"
    MANAGE_KNOWLEDGE = "MANAGE_KNOWLEDGE"
    MANAGE_MEMORY = "MANAGE_MEMORY"
    GENERATE_PROPOSAL = "GENERATE_PROPOSAL"
    CREATE_BRIEFING = "CREATE_BRIEFING"


class Permission(str, Enum):
    READ_RESEARCH = "READ_RESEARCH"
    WRITE_RESEARCH = "WRITE_RESEARCH"
    READ_KNOWLEDGE = "READ_KNOWLEDGE"
    WRITE_KNOWLEDGE = "WRITE_KNOWLEDGE"
    READ_MEMORY = "READ_MEMORY"
    WRITE_MEMORY = "WRITE_MEMORY"
    CREATE_DRAFT = "CREATE_DRAFT"
    REVIEW_DRAFT = "REVIEW_DRAFT"
    READ_ANALYTICS = "READ_ANALYTICS"
    PUBLISH_APPROVED = "PUBLISH_APPROVED"
    USE_EXTERNAL_WEB = "USE_EXTERNAL_WEB"
    USE_LLM = "USE_LLM"
    USE_VOICE_API = "USE_VOICE_API"
    BLOCK_WORKFLOW = "BLOCK_WORKFLOW"
    CREATE_PLANNING_REQUEST = "CREATE_PLANNING_REQUEST"


class MemoryScope(str, Enum):
    NONE = "NONE"
    TASK_ONLY = "TASK_ONLY"
    AGENT_PRIVATE = "AGENT_PRIVATE"
    PROJECT_SHARED = "PROJECT_SHARED"
    KNOWLEDGE_READ = "KNOWLEDGE_READ"
    KNOWLEDGE_WRITE = "KNOWLEDGE_WRITE"
    FOUNDER_PRIVATE = "FOUNDER_PRIVATE"
    SYSTEM_PRIVATE = "SYSTEM_PRIVATE"


class AutonomyLevel(IntEnum):
    DISABLED = 0
    SUGGESTION_ONLY = 1
    INTERNAL_EXECUTION = 2
    CONTROLLED_EXTERNAL_EXECUTION = 3


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FailureCategory(str, Enum):
    MODEL_ERROR = "MODEL_ERROR"
    TOOL_ERROR = "TOOL_ERROR"
    TIMEOUT = "TIMEOUT"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    MEMORY_ERROR = "MEMORY_ERROR"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"


@dataclass(frozen=True)
class ModelConfiguration:
    provider: str
    model: str
    temperature: float = 0.0
    max_output: int = 4096
    timeout_seconds: int = 60
    tool_mode: str = "explicit"
    structured_output_schema: str | None = None
    fallback_provider: str | None = None


@dataclass(frozen=True)
class Budget:
    tasks_per_minute: int = 10
    tool_calls_per_minute: int = 30
    token_budget: int = 20_000
    cost_budget: float = 5.0
    daily_budget: float = 50.0


@dataclass(frozen=True)
class AuditMetadata:
    created_by: str
    approved_by: str | None = None
    approval_reference: str | None = None


@dataclass(frozen=True)
class AgentManifest:
    agent_id: str
    agent_name: str
    agent_type: AgentType
    version: str
    description: str
    role: str
    autonomy_level: AutonomyLevel
    capabilities: frozenset[Capability]
    permissions: frozenset[Permission]
    memory_scopes: frozenset[MemoryScope]
    tools: frozenset[str]
    prompt_id: str
    model_profile: ModelConfiguration
    owner: str
    audit_metadata: AuditMetadata
    constraints: tuple[str, ...] = ()
    max_concurrency: int = 1
    timeout_seconds: int = 60
    budget: Budget = field(default_factory=Budget)
    status: AgentStatus = AgentStatus.REGISTERED
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    last_active_at: datetime | None = None
    health_status: HealthStatus = HealthStatus.OFFLINE

    def validate(self) -> None:
        if not self.agent_id or not self.agent_name or not self.role or not self.owner:
            raise ValueError("agent identity, role, and owner are required")
        if not self.version or not all(p.isdigit() for p in self.version.split(".")):
            raise ValueError("version must contain dot-separated integers")
        if not self.prompt_id or not self.model_profile.provider or not self.model_profile.model:
            raise ValueError("prompt and model provider configuration are required")
        if self.autonomy_level == AutonomyLevel.DISABLED and self.status == AgentStatus.READY:
            raise ValueError("disabled autonomy cannot be READY")
        if self.autonomy_level > AutonomyLevel.CONTROLLED_EXTERNAL_EXECUTION:
            raise ValueError("autonomy level 4 is reserved")
        if self.max_concurrency < 1 or self.timeout_seconds < 1:
            raise ValueError("concurrency and timeout must be positive")
        if MemoryScope.NONE in self.memory_scopes and len(self.memory_scopes) > 1:
            raise ValueError("NONE memory scope cannot be combined")


@dataclass(frozen=True)
class ToolDefinition:
    tool_id: str
    category: str
    risk_level: RiskLevel
    allowed_agent_types: frozenset[AgentType]
    required_permissions: frozenset[Permission]
    calls_per_minute: int
    audit_policy: str = "ALL_CALLS"


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    workflow_id: str
    agent_id: str
    goal: str
    input: Mapping[str, Any]
    context: Mapping[str, Any]
    constraints: tuple[str, ...]
    allowed_tools: frozenset[str]
    expected_output: Mapping[str, Any]
    timeout_seconds: int
    priority: int
    risk_level: RiskLevel
    created_at: datetime = field(default_factory=utcnow)
    guardian_approved: bool = True


class ResultStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class AgentResult:
    task_id: str
    agent_id: str
    status: ResultStatus
    output: Mapping[str, Any]
    confidence: float
    evidence: tuple[Mapping[str, Any], ...] = ()
    tool_usage: tuple[Mapping[str, Any], ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    suggested_next_step: str | None = None
    execution_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class HealthMetrics:
    heartbeat: datetime | None = None
    last_successful_task: datetime | None = None
    failures: int = 0
    total_tasks: int = 0
    average_latency_ms: float = 0
    invalid_outputs: int = 0
    tool_errors: int = 0
    timeouts: int = 0
    policy_violations: int = 0
    state: HealthStatus = HealthStatus.OFFLINE


@dataclass(frozen=True)
class AuditRecord:
    event: str
    actor: str
    agent_id: str | None
    workflow_id: str | None = None
    task_id: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=utcnow)
    record_id: str = field(default_factory=lambda: str(uuid4()))


class ModelProvider(Protocol):
    @property
    def provider_id(self) -> str: ...
    def execute(self, task: AgentTask, context: Mapping[str, Any], config: ModelConfiguration) -> AgentResult: ...
