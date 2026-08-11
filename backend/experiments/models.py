"""Domain objects for controlled, auditable experiments (stdlib only)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def identifier(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class Status(StrEnum):
    IDEA = "IDEA"
    DESIGNED = "DESIGNED"
    READY_FOR_APPROVAL = "READY_FOR_APPROVAL"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COLLECTING_RESULTS = "COLLECTING_RESULTS"
    EVALUATING = "EVALUATING"
    REVIEW = "REVIEW"
    COMPLETED = "COMPLETED"
    KNOWLEDGE_UPDATED = "KNOWLEDGE_UPDATED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConfidenceLabel(StrEnum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class ExperimentType(StrEnum):
    AI_TOOL_REVIEW = "AI_TOOL_REVIEW"
    MODEL_COMPARISON = "MODEL_COMPARISON"
    PROMPT_TEST = "PROMPT_TEST"
    IMAGE_TEST = "IMAGE_TEST"
    VIDEO_TEST = "VIDEO_TEST"
    VOICE_TEST = "VOICE_TEST"
    CODING_TEST = "CODING_TEST"
    AUTOMATION_TEST = "AUTOMATION_TEST"
    PRODUCTIVITY_TEST = "PRODUCTIVITY_TEST"
    QUALITY_TEST = "QUALITY_TEST"
    LATENCY_TEST = "LATENCY_TEST"
    COST_TEST = "COST_TEST"
    RELIABILITY_TEST = "RELIABILITY_TEST"
    USABILITY_TEST = "USABILITY_TEST"
    REGRESSION_TEST = "REGRESSION_TEST"


class EvidenceType(StrEnum):
    TEXT_OUTPUT = "TEXT_OUTPUT"
    IMAGE_OUTPUT = "IMAGE_OUTPUT"
    VIDEO_OUTPUT = "VIDEO_OUTPUT"
    AUDIO_OUTPUT = "AUDIO_OUTPUT"
    SCREENSHOT = "SCREENSHOT"
    LOG = "LOG"
    METRIC = "METRIC"
    API_RESPONSE = "API_RESPONSE"
    TIMING = "TIMING"
    ERROR = "ERROR"
    HUMAN_RATING = "HUMAN_RATING"
    SYSTEM_RATING = "SYSTEM_RATING"


@dataclass(slots=True)
class Environment:
    operating_environment: str
    experiment_date: str
    tool_version: str
    api_version: str | None = None
    model_version: str | None = None
    subscription_tier: str | None = None
    region: str | None = None
    language: str | None = None
    input_files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    browser_app_version: str | None = None
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Cost:
    subscription: float = 0
    api: float = 0
    tokens: float = 0
    generation: float = 0
    compute: float = 0
    time: float = 0
    other: float = 0
    estimated_total: float = 0
    actual_total: float = 0

    def calculated(self) -> float:
        values = (self.subscription, self.api, self.tokens, self.generation,
                  self.compute, self.time, self.other)
        if any(value < 0 for value in values):
            raise ValueError("cost components cannot be negative")
        return round(sum(values), 6)


@dataclass(slots=True)
class Rubric:
    name: str
    description: str
    scale: tuple[float, float]
    criteria: dict[str, str]
    version: int = 1
    evaluator_type: str = "HUMAN"
    id: str = field(default_factory=lambda: identifier("rub"))


@dataclass(slots=True)
class Metric:
    name: str
    description: str
    unit: str
    evaluation_method: str
    higher_is_better: bool = True
    weight: float = 1
    raw_value: float | None = None
    normalized_value: float | None = None
    confidence: float = 0
    evaluator: str = "objective"
    rubric: Rubric | None = None
    id: str = field(default_factory=lambda: identifier("met"))

    def normalize(self, minimum: float, maximum: float) -> float:
        if maximum <= minimum or self.raw_value is None:
            raise ValueError("valid bounds and a raw value are required")
        value = min(1.0, max(0.0, (self.raw_value - minimum) / (maximum - minimum)))
        self.normalized_value = value if self.higher_is_better else 1 - value
        return self.normalized_value


@dataclass(slots=True)
class Evidence:
    type: EvidenceType
    storage_reference: str
    checksum: str
    source: str
    test_case_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    confidentiality: str = "INTERNAL"
    id: str = field(default_factory=lambda: identifier("ev"))
    created_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class TestResult:
    status: str
    text: str | None = None
    numeric_metrics: dict[str, float] = field(default_factory=dict)
    file_references: list[str] = field(default_factory=list)
    notes: str | None = None
    human_ratings: dict[str, float] = field(default_factory=dict)
    raw_vendor_result: Any = None
    attempts: int = 1
    failures: int = 0


@dataclass(slots=True)
class TestCase:
    title: str
    goal: str
    input: dict[str, Any]
    expected_behavior: str
    evaluation_method: str
    required_tools: list[str]
    execution_order: int
    repeat_count: int = 1
    id: str = field(default_factory=lambda: identifier("tc"))
    status: str = "PENDING"
    result: TestResult | None = None
    notes: str | None = None

    def validate(self) -> None:
        if not self.title.strip() or not self.goal.strip() or not self.evaluation_method.strip():
            raise ValueError("test case title, goal, and evaluation method are required")
        if self.repeat_count < 1 or self.execution_order < 0:
            raise ValueError("invalid repeat count or execution order")


@dataclass(slots=True)
class Protocol:
    question: str
    hypothesis: str | None
    inputs: list[dict[str, Any]]
    settings: dict[str, Any]
    sample_size: int
    approval_requirements: list[str]
    benchmark: str | None = None
    version: int = 1

    def validate(self, test_cases: list[TestCase], metrics: list[Metric]) -> None:
        if not self.question.strip() or self.sample_size < 1:
            raise ValueError("question and positive sample size are required")
        if not test_cases or not metrics:
            raise ValueError("protocol requires test cases and metrics")
        for case in test_cases:
            case.validate()
        if self.sample_size != sum(c.repeat_count for c in test_cases):
            raise ValueError("sample size must equal all planned repetitions")


@dataclass(slots=True)
class HistoryEntry:
    version: int
    action: str
    actor: str
    at: datetime
    snapshot: dict[str, Any]


@dataclass(slots=True)
class Experiment:
    title: str
    description: str
    tool: str
    provider: str
    category: str
    experiment_type: ExperimentType
    owner: str
    created_by: str
    environment: Environment
    protocol: Protocol
    test_cases: list[TestCase]
    metrics: list[Metric]
    risk: RiskLevel = RiskLevel.LOW
    cost: Cost = field(default_factory=Cost)
    tool_permissions: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: identifier("exp"))
    created_at: datetime = field(default_factory=utcnow)
    approved_by: str | None = None
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    status: Status = Status.IDEA
    version: int = 1
    evidence: list[Evidence] = field(default_factory=list)
    conclusion: str | None = None
    confidence: ConfidenceLabel = ConfidenceLabel.VERY_LOW
    limitations: list[str] = field(default_factory=list)
    knowledge_references: list[str] = field(default_factory=list)
    memory_references: list[str] = field(default_factory=list)
    history: list[HistoryEntry] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("history", None)
        return data


@dataclass(slots=True)
class Comparison:
    experiment_ids: list[str]
    tools: list[str]
    shared_metrics: list[str]
    normalized_results: dict[str, dict[str, float]]
    winner_by_metric: dict[str, str | None]
    tradeoffs: list[str]
    overall_result: str
    confidence: ConfidenceLabel
    limitations: list[str]
    id: str = field(default_factory=lambda: identifier("cmp"))
