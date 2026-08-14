"""Pydantic models for the Growth Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class GrowthConfig(CoreConfig):
    """External configuration for the Growth Engine."""

    required_environment_key: str = Field(min_length=1)


class GrowthStatus(StrEnum):
    """Lifecycle status values for the Growth Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class GrowthContract(BaseModel):
    """Architecture output contract for the Growth Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: GrowthStatus = GrowthStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
