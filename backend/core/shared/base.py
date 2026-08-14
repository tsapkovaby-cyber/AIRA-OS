"""Shared architectural primitives for AIRA Core engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class CoreConfig(BaseModel):
    """Common configuration inherited by every engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str = Field(min_length=1)
    enabled: bool = True


class InitializationResult(BaseModel):
    """Standard result returned when an engine initializes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine_name: str
    initialized: bool


ConfigT = TypeVar("ConfigT", bound=CoreConfig)


class EngineInterface(ABC, Generic[ConfigT]):
    """Interface all AIRA Core engines must implement."""

    @property
    @abstractmethod
    def config(self) -> ConfigT:
        """Return external configuration for this engine."""

    @abstractmethod
    def initialize(self) -> InitializationResult:
        """Initialize the engine without executing business logic."""
