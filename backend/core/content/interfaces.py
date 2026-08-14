"""Interfaces for the Content Engine."""

from __future__ import annotations

from abc import abstractmethod

from backend.core.shared.base import EngineInterface
from backend.core.content.models import ContentConfig, ContentWorkflow


class ContentInterface(EngineInterface[ContentConfig]):
    """Abstract contract for the Content Engine."""

    @abstractmethod
    def describe_contract(self) -> ContentWorkflow:
        """Return the architectural contract without business logic."""
