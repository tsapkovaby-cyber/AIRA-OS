"""Pydantic models for the Research Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class ResearchConfig(CoreConfig):
    """External configuration for the Research Engine."""

    required_environment_key: str = Field(min_length=1)


class ResearchStatus(StrEnum):
    """Lifecycle status values for the Research Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class ResearchContract(BaseModel):
    """Architecture output contract for the Research Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: ResearchStatus = ResearchStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
