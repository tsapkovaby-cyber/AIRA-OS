from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Capability(StrEnum):
    TEXT_GENERATION = "TEXT_GENERATION"
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"
    TOOL_USE = "TOOL_USE"
    VISION = "VISION"
    EMBEDDINGS = "EMBEDDINGS"
    LONG_CONTEXT = "LONG_CONTEXT"
    REASONING = "REASONING"
    FAST_RESPONSE = "FAST_RESPONSE"
    LOW_COST = "LOW_COST"
    MULTILINGUAL = "MULTILINGUAL"
    CODE = "CODE"
    AUDIO_INPUT = "AUDIO_INPUT"
    AUDIO_OUTPUT = "AUDIO_OUTPUT"


class Sensitivity(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    FOUNDER_PRIVATE = "FOUNDER_PRIVATE"
    SYSTEM_SECRET = "SYSTEM_SECRET"


class HealthState(StrEnum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"


class RoutingPolicy(StrEnum):
    QUALITY_FIRST = "QUALITY_FIRST"
    BALANCED = "BALANCED"
    LOW_COST = "LOW_COST"
    LOW_LATENCY = "LOW_LATENCY"
    PRIVACY_FIRST = "PRIVACY_FIRST"
    FOUNDER_SELECTED = "FOUNDER_SELECTED"
    CRITICAL_REVIEW = "CRITICAL_REVIEW"


class ProviderErrorCode(StrEnum):
    TIMEOUT = "PROVIDER_TIMEOUT"
    RATE_LIMIT = "PROVIDER_RATE_LIMIT"
    AUTH_ERROR = "PROVIDER_AUTH_ERROR"
    BAD_REQUEST = "PROVIDER_BAD_REQUEST"
    UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    CONTENT_ERROR = "PROVIDER_CONTENT_ERROR"
    UNKNOWN = "PROVIDER_UNKNOWN_ERROR"


class ProviderError(RuntimeError):
    def __init__(self, code: ProviderErrorCode, message: str = "provider request failed"):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CostProfile:
    input_per_1k: float = 0
    output_per_1k: float = 0

    def estimate(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.input_per_1k + output_tokens * self.output_per_1k) / 1000


@dataclass
class ProviderHealth:
    state: HealthState = HealthState.HEALTHY
    latency_ms: float = 0
    error_rate: float = 0
    recent_failures: int = 0
    success_rate: float = 1
    last_health_check: str | None = None


@dataclass(frozen=True)
class ModelProfile:
    profile_id: str
    provider: str
    model_id: str
    capabilities: frozenset[Capability]
    context_limit: int
    cost: CostProfile = CostProfile()
    latency_ms: int = 1000
    reliability: float = 1
    status: str = "ACTIVE"
    fallback_profiles: tuple[str, ...] = ()
    allowed_sensitivity: Sensitivity = Sensitivity.INTERNAL
    evaluation_scores: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.profile_id or self.context_limit <= 0 or not 0 <= self.reliability <= 1:
            raise ValueError("invalid model profile")


@dataclass(frozen=True)
class TaskProfile:
    profile_id: str
    required_capabilities: frozenset[Capability]
    preferred_qualities: frozenset[Capability] = frozenset()
    maximum_cost: float | None = None
    maximum_latency_ms: int | None = None
    minimum_reliability: float = 0
    fallback_allowed: bool = True
    sensitivity: Sensitivity = Sensitivity.INTERNAL
    output_schema: dict[str, Any] | None = None
    policy: RoutingPolicy = RoutingPolicy.BALANCED


@dataclass(frozen=True)
class RoutingRequest:
    task_id: str
    task_profile: str
    agent_id: str
    context_tokens: int = 0
    input_tokens: int = 0
    expected_output_tokens: int = 0
    workflow_id: str | None = None
    founder_preference: str | None = None


@dataclass(frozen=True)
class RouteDecision:
    provider: str
    model_profile: str
    fallback_chain: tuple[str, ...]
    expected_cost: float
    expected_latency_ms: int
    reason: str
    confidence: float
    alternatives: tuple[str, ...] = ()


@dataclass(frozen=True)
class InferenceResult:
    inference_id: str
    content: Any
    model_profile: str
    fallback_used: bool
    cost: float
    attempts: int

