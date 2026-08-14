"""Interfaces for the Decision Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.decision.models import DecisionConfig, DecisionPlan


class DecisionInterface(EngineInterface[DecisionConfig]):
    """Abstract contract for the Decision Engine."""

    @abstractmethod
    def describe_contract(self) -> DecisionPlan:
        """Return the architectural contract without business logic."""
