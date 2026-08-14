"""Interfaces for the Identity Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.identity.models import IdentityConfig, IdentityObject


class IdentityInterface(EngineInterface[IdentityConfig]):
    """Abstract contract for the Identity Engine."""

    @abstractmethod
    def describe_contract(self) -> IdentityObject:
        """Return the architectural contract without business logic."""
