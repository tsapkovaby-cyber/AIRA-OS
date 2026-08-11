"""Visual provider contract and capability-based routing."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any
from .models import VisualGenerationRequest


class VisualGenerationProvider(Protocol):
    name: str
    def generate_image(self, request: VisualGenerationRequest, prompt: str) -> list[dict[str, Any]]: ...
    def edit_image(self, asset_id: str, instructions: str) -> dict[str, Any]: ...
    def generate_variations(self, asset_id: str, count: int) -> list[dict[str, Any]]: ...
    def get_capabilities(self) -> set[str]: ...
    def estimate_cost(self, request: VisualGenerationRequest) -> float: ...
    def health_check(self) -> bool: ...


@dataclass(frozen=True)
class ProviderProfile:
    provider: VisualGenerationProvider
    founder_approved: bool
    privacy_level: str
    data_retention_policy: str
    training_usage_policy: str
    commercial_use_notes: str
    region: str


class VisualModelRouter:
    def __init__(self, profiles: list[ProviderProfile]): self.profiles = profiles

    def route(self, required: set[str], request: VisualGenerationRequest) -> VisualGenerationProvider:
        eligible = [p.provider for p in self.profiles if p.founder_approved and p.provider.health_check() and required <= p.provider.get_capabilities()]
        if not eligible:
            raise LookupError("no Founder-approved provider satisfies visual task")
        affordable = [(p.estimate_cost(request), p) for p in eligible if p.estimate_cost(request) <= request.cost_limit]
        if not affordable:
            raise PermissionError("WAITING_FOUNDER_APPROVAL: provider cost exceeds request limit")
        return min(affordable, key=lambda item: item[0])[1]
