"""Pydantic models for the Memory Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class MemoryConfig(CoreConfig):
    """External configuration for the Memory Engine."""

    required_environment_key: str = Field(min_length=1)


class MemoryStatus(StrEnum):
    """Lifecycle status values for the Memory Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class MemoryContract(BaseModel):
    """Architecture output contract for the Memory Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: MemoryStatus = MemoryStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
