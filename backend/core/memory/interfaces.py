"""Interfaces for the Memory Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.memory.models import MemoryConfig, MemoryContract


class MemoryInterface(EngineInterface[MemoryConfig]):
    """Abstract contract for the Memory Engine."""

    @abstractmethod
    def describe_contract(self) -> MemoryContract:
        """Return the architectural contract without business logic."""
