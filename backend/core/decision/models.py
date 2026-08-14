"""Pydantic models for the Decision Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class DecisionConfig(CoreConfig):
    """External configuration for the Decision Engine."""

    required_environment_key: str = Field(min_length=1)


class DecisionStatus(StrEnum):
    """Lifecycle status values for the Decision Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class DecisionPlan(BaseModel):
    """Architecture output contract for the Decision Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: DecisionStatus = DecisionStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
