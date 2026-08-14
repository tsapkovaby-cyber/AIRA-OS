"""Interfaces for the Research Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.research.models import ResearchConfig, ResearchContract


class ResearchInterface(EngineInterface[ResearchConfig]):
    """Abstract contract for the Research Engine."""

    @abstractmethod
    def describe_contract(self) -> ResearchContract:
        """Return the architectural contract without business logic."""
