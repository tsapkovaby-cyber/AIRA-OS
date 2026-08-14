"""Minimal initializer for the Content Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.content.interfaces import ContentInterface
from backend.core.content.models import ContentConfig, ContentStatus, ContentWorkflow


class ContentEngine(ContentInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: ContentConfig) -> None:
        self._config = config

    @property
    def config(self) -> ContentConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> ContentWorkflow:
        return ContentWorkflow(
            engine_name=self.config.engine_name,
            status=ContentStatus.INITIALIZED,
            responsibility_summary="Represent research to publishing queue stages without generation business logic.",
        )
