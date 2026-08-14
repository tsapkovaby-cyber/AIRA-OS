"""Pydantic models for the Guardian Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class GuardianConfig(CoreConfig):
    """External configuration for the Guardian Engine."""

    required_environment_key: str = Field(min_length=1)


class GuardianStatus(StrEnum):
    """Lifecycle status values for the Guardian Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class GuardianPolicy(BaseModel):
    """Architecture output contract for the Guardian Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: GuardianStatus = GuardianStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
