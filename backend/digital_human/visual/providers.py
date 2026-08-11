from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .domain import VisualGenerationRequest
from .prompts import AssembledPrompt


@dataclass(frozen=True)
class ProviderCapabilities:
    features: frozenset[str]
    max_resolution: str


@dataclass(frozen=True)
class ProviderOutput:
    provider_generation_id: str
    model: str
    file_reference: str
    sha256: str


class VisualGenerationProvider(Protocol):
    provider_id: str
    data_retention_policy: str
    training_usage_policy: str
    founder_approved: bool

    def generate_image(self, request: VisualGenerationRequest, prompt: AssembledPrompt) -> list[ProviderOutput]: ...
    def edit_image(self, source_file_reference: str, prompt: AssembledPrompt) -> ProviderOutput: ...
    def generate_variations(self, source_file_reference: str, count: int) -> list[ProviderOutput]: ...
    def get_capabilities(self) -> ProviderCapabilities: ...
    def estimate_cost(self, request: VisualGenerationRequest) -> float: ...
    def health_check(self) -> bool: ...


class VisualModelRouter:
    def __init__(self, providers: list[VisualGenerationProvider]) -> None:
        self.providers = providers

    def route(self, request: VisualGenerationRequest) -> VisualGenerationProvider:
        candidates = []
        for provider in self.providers:
            allowed = request.provider_policy.allowed_provider_ids
            if (not allowed or provider.provider_id in allowed) and provider.founder_approved and provider.health_check():
                if request.provider_policy.required_capabilities <= provider.get_capabilities().features:
                    candidates.append(provider)
        affordable = [p for p in candidates if p.estimate_cost(request) <= request.cost_limit]
        if not affordable:
            raise LookupError("no approved, healthy, capable provider within request budget")
        return min(affordable, key=lambda p: p.estimate_cost(request))
