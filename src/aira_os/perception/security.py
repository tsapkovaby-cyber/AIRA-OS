"""Guardian boundary for untrusted media and provider privacy permissions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Confidence, Observation, PerceptionRequest, PerceptionResult, PrivacyLevel


class PerceptionSecurityError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderPermission:
    provider: str
    privacy_levels: frozenset[PrivacyLevel]


class PerceptionGuardian:
    """Enforces privacy, lineage, and the media-as-data trust boundary."""

    INJECTION_MARKERS = (
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "you are now",
        "developer message",
    )

    def __init__(self, permissions: Iterable[ProviderPermission] = ()) -> None:
        self._permissions = {item.provider: item.privacy_levels for item in permissions}

    def authorize_provider(self, provider: str, request: PerceptionRequest) -> None:
        if request.privacy_level not in self._permissions.get(provider, frozenset()):
            raise PerceptionSecurityError(
                f"provider {provider!r} is not approved for {request.privacy_level.value}"
            )

    def inspect(self, result: PerceptionResult) -> PerceptionResult:
        source_ids = {asset.asset_id for asset in result.source_references}
        if any(obs.source_id not in source_ids for obs in result.observations):
            raise PerceptionSecurityError("observation source lineage is missing")
        # Embedded commands remain labelled observations and are never dispatched.
        return result

    def classify_content(self, content: str) -> tuple[str, Confidence, tuple[str, ...]]:
        lowered = content.casefold()
        if any(marker in lowered for marker in self.INJECTION_MARKERS):
            return "untrusted_embedded_instruction", Confidence.HIGH_CONFIDENCE, (
                "Potential prompt injection retained as inert source data.",
            )
        return "content", Confidence.MEDIUM_CONFIDENCE, ()
