"""Pydantic models for the Content Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class ContentConfig(CoreConfig):
    """External configuration for the Content Engine."""

    required_environment_key: str = Field(min_length=1)


class ContentStatus(StrEnum):
    """Lifecycle status values for the Content Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class ContentWorkflow(BaseModel):
    """Architecture output contract for the Content Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: ContentStatus = ContentStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
