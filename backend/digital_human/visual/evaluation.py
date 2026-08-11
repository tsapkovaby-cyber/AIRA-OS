from typing import Protocol

from .domain import EvaluationResult, VisualAsset


class IdentityEvaluator(Protocol):
    """Implementations may combine embeddings, feature models, experiments and human review."""
    def evaluate(self, asset: VisualAsset) -> EvaluationResult: ...


class VisualGuardian(Protocol):
    def review(self, asset: VisualAsset, evaluation: EvaluationResult) -> tuple[bool, tuple[str, ...]]: ...


class ThresholdGuardian:
    def __init__(self, identity_accept: float = 80, identity_review: float = 70, quality_accept: float = 80) -> None:
        self.identity_accept = identity_accept
        self.identity_review = identity_review
        self.quality_accept = quality_accept

    def review(self, asset: VisualAsset, evaluation: EvaluationResult) -> tuple[bool, tuple[str, ...]]:
        reasons = list(evaluation.identity_reasons + evaluation.quality_defects)
        if evaluation.identity_score < self.identity_accept:
            reasons.append("identity threshold not met")
        if evaluation.quality_score < self.quality_accept:
            reasons.append("quality threshold not met")
        return not reasons, tuple(reasons)
