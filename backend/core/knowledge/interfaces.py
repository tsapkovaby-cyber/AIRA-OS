"""Interfaces for the Knowledge Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.knowledge.models import KnowledgeConfig, KnowledgeContract


class KnowledgeInterface(EngineInterface[KnowledgeConfig]):
    """Abstract contract for the Knowledge Engine."""

    @abstractmethod
    def describe_contract(self) -> KnowledgeContract:
        """Return the architectural contract without business logic."""
