"""Minimal initializer for the Guardian Engine."""

from __future__ import annotations

from backend.core.shared.base import InitializationResult
from backend.core.guardian.interfaces import GuardianInterface
from backend.core.guardian.models import GuardianConfig, GuardianStatus, GuardianPolicy


class GuardianEngine(GuardianInterface):
    """Architecture-only implementation for initialization and validation."""

    def __init__(self, config: GuardianConfig) -> None:
        self._config = config

    @property
    def config(self) -> GuardianConfig:
        return self._config

    def initialize(self) -> InitializationResult:
        return InitializationResult(engine_name=self.config.engine_name, initialized=self.config.enabled)

    def describe_contract(self) -> GuardianPolicy:
        return GuardianPolicy(
            engine_name=self.config.engine_name,
            status=GuardianStatus.INITIALIZED,
            responsibility_summary="Represent constitution, transparency, evidence, approval, safety, and tone checks.",
        )
