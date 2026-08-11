"""Minimal initializer for the Identity Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.identity.interfaces import IdentityInterface
from backend.core.identity.models import IdentityConfig, IdentityStatus, IdentityObject


class IdentityEngine(IdentityInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: IdentityConfig) -> None:
        self._config = config

    @property
    def config(self) -> IdentityConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> IdentityObject:
        return IdentityObject(
            engine_name=self.config.engine_name,
            status=IdentityStatus.INITIALIZED,
            responsibility_summary="Load identity configuration, personality, values, communication style, mission, and constitution.",
        )
