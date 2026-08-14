"""Minimal initializer for the Decision Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.decision.interfaces import DecisionInterface
from backend.core.decision.models import DecisionConfig, DecisionStatus, DecisionPlan


class DecisionEngine(DecisionInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: DecisionConfig) -> None:
        self._config = config

    @property
    def config(self) -> DecisionConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> DecisionPlan:
        return DecisionPlan(
            engine_name=self.config.engine_name,
            status=DecisionStatus.INITIALIZED,
            responsibility_summary="Receive requests, select workflows, apply rules, and identify research or approval needs.",
        )
