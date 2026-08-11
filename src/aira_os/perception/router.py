"""Privacy-aware task/cost/capability multimodal provider routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import MediaType, PerceptionRequest, PrivacyLevel
from .security import PerceptionGuardian


TASK_PROFILES = frozenset({
    "aira_image_review", "aira_video_review", "aira_tool_screenshot",
    "aira_document_analysis", "aira_voice_message", "aira_content_review",
    "aira_identity_review", "aira_experiment_evidence",
})


@dataclass(frozen=True)
class ProviderRegistration:
    provider: Any
    media_types: frozenset[MediaType]
    privacy_levels: frozenset[PrivacyLevel]
    tasks: frozenset[str] = TASK_PROFILES
    cost_rank: int = 0
    latency_rank: int = 0
    accuracy_rank: int = 0


class MultimodalRouter:
    def __init__(self, registrations: tuple[ProviderRegistration, ...], guardian: PerceptionGuardian) -> None:
        self.registrations = registrations
        self.guardian = guardian

    def select(self, request: PerceptionRequest) -> Any:
        task = str(request.context.get("task_profile", "aira_content_review"))
        candidates = [r for r in self.registrations if request.media_type in r.media_types
                      and request.privacy_level in r.privacy_levels and task in r.tasks]
        if not candidates:
            raise LookupError("no approved provider satisfies media, task, and privacy policy")
        preference = str(request.model_policy.get("optimize", "accuracy"))
        key = (lambda r: r.cost_rank) if preference == "cost" else (
            (lambda r: r.latency_rank) if preference == "latency" else (lambda r: -r.accuracy_rank)
        )
        selected = sorted(candidates, key=key)[0].provider
        self.guardian.authorize_provider(selected.name, request)
        return selected
