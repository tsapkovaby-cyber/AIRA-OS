"""Interfaces for the Guardian Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.guardian.models import GuardianConfig, GuardianPolicy


class GuardianInterface(EngineInterface[GuardianConfig]):
    """Abstract contract for the Guardian Engine."""

    @abstractmethod
    def describe_contract(self) -> GuardianPolicy:
        """Return the architectural contract without business logic."""
