"""Minimal initializer for the Research Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.research.interfaces import ResearchInterface
from backend.core.research.models import ResearchConfig, ResearchStatus, ResearchContract


class ResearchEngine(ResearchInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: ResearchConfig) -> None:
        self._config = config

    @property
    def config(self) -> ResearchConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> ResearchContract:
        return ResearchContract(
            engine_name=self.config.engine_name,
            status=ResearchStatus.INITIALIZED,
            responsibility_summary="Define research requests and results without internet integration or automation.",
        )
