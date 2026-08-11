"""Minimal initializer for the Growth Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.growth.interfaces import GrowthInterface
from backend.core.growth.models import GrowthConfig, GrowthStatus, GrowthContract


class GrowthEngine(GrowthInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: GrowthConfig) -> None:
        self._config = config

    @property
    def config(self) -> GrowthConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> GrowthContract:
        return GrowthContract(
            engine_name=self.config.engine_name,
            status=GrowthStatus.INITIALIZED,
            responsibility_summary="Define improvement-analysis interfaces without implementation.",
        )
