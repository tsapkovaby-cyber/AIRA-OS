"""Interfaces for the Growth Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.growth.models import GrowthConfig, GrowthContract


class GrowthInterface(EngineInterface[GrowthConfig]):
    """Abstract contract for the Growth Engine."""

    @abstractmethod
    def describe_contract(self) -> GrowthContract:
        """Return the architectural contract without business logic."""
