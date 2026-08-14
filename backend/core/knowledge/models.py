"""Pydantic models for the Knowledge Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class KnowledgeConfig(CoreConfig):
    """External configuration for the Knowledge Engine."""

    required_environment_key: str = Field(min_length=1)


class KnowledgeStatus(StrEnum):
    """Lifecycle status values for the Knowledge Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class KnowledgeContract(BaseModel):
    """Architecture output contract for the Knowledge Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: KnowledgeStatus = KnowledgeStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
