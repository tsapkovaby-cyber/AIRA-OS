"""Explicit, reviewable candidate sinks for downstream AIRA subsystems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import PerceptionRequest, PerceptionResult


@dataclass(frozen=True)
class PerceptionCandidate:
    kind: str
    request_id: str
    result_id: str
    source_ids: tuple[str, ...]
    requires_guardian_review: bool = True


class CandidateSink(Protocol):
    def submit(self, candidate: PerceptionCandidate) -> None: ...


class PerceptionIntegrations:
    def __init__(self, *, knowledge: CandidateSink | None = None, memory: CandidateSink | None = None,
                 experiment: CandidateSink | None = None, reasoning: CandidateSink | None = None) -> None:
        self.sinks = {"knowledge": knowledge, "memory": memory, "experiment": experiment,
                      "reasoning": reasoning}

    def publish(self, request: PerceptionRequest, result: PerceptionResult) -> None:
        source_ids = tuple(asset.asset_id for asset in result.source_references)
        requested = {"reasoning"}
        requested.update(str(x) for x in request.context.get("candidate_sinks", ()))
        if request.context.get("experiment_id"):
            requested.add("experiment")
        for kind in requested:
            sink = self.sinks.get(kind)
            if sink:
                sink.submit(PerceptionCandidate(kind, request.request_id, result.result_id, source_ids))
