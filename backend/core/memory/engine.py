"""Minimal initializer for the Memory Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.memory.interfaces import MemoryInterface
from backend.core.memory.models import MemoryConfig, MemoryStatus, MemoryContract


class MemoryEngine(MemoryInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: MemoryConfig) -> None:
        self._config = config

    @property
    def config(self) -> MemoryConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> MemoryContract:
        return MemoryContract(
            engine_name=self.config.engine_name,
            status=MemoryStatus.INITIALIZED,
            responsibility_summary="Expose interfaces for identity, knowledge, experience, conversation, and user-preference memory.",
        )
