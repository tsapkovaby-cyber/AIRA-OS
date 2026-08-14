from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from .domain import Capability, CostProfile, HealthState, ProviderError, ProviderErrorCode, ProviderHealth


class IntelligenceProvider(ABC):
    """Adapter boundary. Implementations contain transport logic, never AIRA identity."""

    @abstractmethod
    def generate(self, prompt: list[dict[str, str]], model: str) -> str: ...

    def generate_structured(self, prompt: list[dict[str, str]], model: str, schema: dict[str, Any]) -> Any:
        return json.loads(self.generate(prompt, model))

    def stream(self, prompt: list[dict[str, str]], model: str) -> Iterator[str]:
        yield self.generate(prompt, model)

    @abstractmethod
    def health_check(self) -> ProviderHealth: ...

    @abstractmethod
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float: ...

    @abstractmethod
    def get_capabilities(self, model: str) -> frozenset[Capability]: ...


class ProviderAdapterSkeleton(IntelligenceProvider):
    """Base for OpenAI/Anthropic/Gemini/local adapters configured outside source."""

    def __init__(self, capabilities=frozenset(), cost: CostProfile = CostProfile()):
        self.capabilities, self.cost = frozenset(capabilities), cost

    def generate(self, prompt, model):
        raise ProviderError(ProviderErrorCode.UNAVAILABLE, "adapter is not configured")

    def health_check(self):
        return ProviderHealth(HealthState.UNAVAILABLE)

    def estimate_cost(self, model, input_tokens, output_tokens):
        return self.cost.estimate(input_tokens, output_tokens)

    def get_capabilities(self, model):
        return self.capabilities


OpenAIProvider = AnthropicProvider = GeminiProvider = LocalProvider = ProviderAdapterSkeleton


class MockIntelligenceProvider(IntelligenceProvider):
    def __init__(self, mode="success", response='{"result":"ok"}', latency_ms=0, capabilities=None):
        self.mode, self.response, self.latency_ms = mode, response, latency_ms
        self.capabilities = frozenset(capabilities or Capability)
        self.calls: list[list[dict[str, str]]] = []

    def generate(self, prompt, model):
        self.calls.append(prompt)
        if self.latency_ms:
            time.sleep(self.latency_ms / 1000)
        errors = {"timeout": ProviderErrorCode.TIMEOUT, "rate_limit": ProviderErrorCode.RATE_LIMIT,
                  "failure": ProviderErrorCode.UNAVAILABLE}
        if self.mode in errors:
            raise ProviderError(errors[self.mode])
        if self.mode == "invalid_schema":
            return "{}"
        if self.mode == "invalid_json":
            return "not-json"
        if self.mode == "empty":
            return ""
        return self.response

    def health_check(self):
        state = HealthState.UNAVAILABLE if self.mode == "unhealthy" else HealthState.HEALTHY
        return ProviderHealth(state=state, latency_ms=self.latency_ms)

    def estimate_cost(self, model, input_tokens, output_tokens):
        return (input_tokens + output_tokens) / 1_000_000

    def get_capabilities(self, model):
        return self.capabilities
