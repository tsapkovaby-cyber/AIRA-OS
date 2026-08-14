"""Minimal initializer for the Knowledge Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.knowledge.interfaces import KnowledgeInterface
from backend.core.knowledge.models import KnowledgeConfig, KnowledgeStatus, KnowledgeContract


class KnowledgeEngine(KnowledgeInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: KnowledgeConfig) -> None:
        self._config = config

    @property
    def config(self) -> KnowledgeConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> KnowledgeContract:
        return KnowledgeContract(
            engine_name=self.config.engine_name,
            status=KnowledgeStatus.INITIALIZED,
            responsibility_summary="Register tool cards, retrieve cards, update versions, track history, and store evaluations.",
        )
