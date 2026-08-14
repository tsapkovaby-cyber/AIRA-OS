"""Pydantic models for the Identity Engine."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.core.shared.base import CoreConfig


class IdentityConfig(CoreConfig):
    """External configuration for the Identity Engine."""

    required_environment_key: str = Field(min_length=1)


class IdentityStatus(StrEnum):
    """Lifecycle status values for the Identity Engine."""

    DECLARED = "declared"
    INITIALIZED = "initialized"


class IdentityObject(BaseModel):
    """Architecture output contract for the Identity Engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    status: IdentityStatus = IdentityStatus.DECLARED
    responsibility_summary: str = Field(min_length=1)
