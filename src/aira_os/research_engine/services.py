"""Architecture services for Research Engine validation and orchestration."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, date, datetime

from .models import (
    Freshness,
    InformationCategory,
    KnowledgeCandidate,
    PipelineStage,
    ResearchItem,
    ResearchScore,
    SourceCategory,
    TrustLevel,
)

TRUST_BASE_CONFIDENCE = {
    TrustLevel.LEVEL_A: 0.9,
    TrustLevel.LEVEL_B: 0.75,
    TrustLevel.LEVEL_C: 0.55,
    TrustLevel.LEVEL_D: 0.2,
}


class ResearchValidationError(ValueError):
    pass


def validate_discovery(item: ResearchItem) -> None:
    required_text = {
        "title": item.title,
        "summary": item.summary,
        "source.name": item.source.name,
        "source.url": item.source.url,
        "language": item.language,
        "security.owner": item.security.owner,
        "security.visibility": item.security.visibility,
    }
    missing = [name for name, value in required_text.items() if not value or not value.strip()]
    if missing:
        raise ResearchValidationError(f"Missing required fields: {', '.join(missing)}")


def classify_source(category: SourceCategory) -> TrustLevel:
    if category in {SourceCategory.OFFICIAL, SourceCategory.ACADEMIC}:
        return TrustLevel.LEVEL_A
    if category in {SourceCategory.DEVELOPER, SourceCategory.INDUSTRY, SourceCategory.INTERNAL}:
        return TrustLevel.LEVEL_B
    if category in {SourceCategory.COMMUNITY, SourceCategory.EXPERIMENTAL}:
        return TrustLevel.LEVEL_C
    return TrustLevel.LEVEL_D


def normalize_item(item: ResearchItem) -> ResearchItem:
    item.title = " ".join(item.title.split())
    item.summary = " ".join(item.summary.split())
    item.tags = {tag.strip().lower().replace(" ", "-") for tag in item.tags if tag.strip()}
    item.history.append("normalized")
    return item


def evaluate_freshness(publication_date: date | None, now: date | None = None) -> Freshness:
    if publication_date is None:
        return Freshness.CURRENT
    today = now or datetime.now(UTC).date()
    age_days = (today - publication_date).days
    if age_days <= 7:
        return Freshness.FRESH
    if age_days <= 30:
        return Freshness.RECENT
    if age_days <= 180:
        return Freshness.CURRENT
    if age_days <= 730:
        return Freshness.OLD
    return Freshness.HISTORICAL


def calculate_confidence(item: ResearchItem) -> float:
    base = TRUST_BASE_CONFIDENCE[item.trust_level or item.source.effective_trust_level()]
    verification_bonus = 0.05 if item.source.verified else 0.0
    reference_bonus = min(len(item.references) * 0.02, 0.1)
    duplicate_penalty = 0.05 if item.duplicate_of else 0.0
    conflict_penalty = min(len(item.conflicts) * 0.1, 0.3)
    return max(0.0, min(1.0, base + verification_bonus + reference_bonus - duplicate_penalty - conflict_penalty))


def score_item(item: ResearchItem, *, practical_importance: float = 0.5, business_impact: float = 0.5, educational_value: float = 0.5, novelty: float = 0.5) -> ResearchScore:
    trust = item.trust_level or item.source.effective_trust_level()
    confidence = calculate_confidence(item)
    source_quality = TRUST_BASE_CONFIDENCE[trust]
    evidence_quality = min(1.0, 0.4 + len(item.references) * 0.15 + (0.2 if item.source.verified else 0))
    item.confidence = confidence
    item.score = ResearchScore(source_quality, evidence_quality, practical_importance, business_impact, educational_value, novelty, confidence)
    return item.score


def duplicate_key(item: ResearchItem) -> tuple[str, str, InformationCategory]:
    normalized_title = " ".join(item.title.lower().split())
    normalized_source = item.source.url.rstrip("/").lower()
    return normalized_title, normalized_source, item.category


def detect_duplicates(items: Iterable[ResearchItem]) -> list[tuple[ResearchItem, ResearchItem]]:
    seen: dict[tuple[str, str, InformationCategory], ResearchItem] = {}
    duplicates: list[tuple[ResearchItem, ResearchItem]] = []
    for item in items:
        key = duplicate_key(item)
        if key in seen:
            original = seen[key]
            item.duplicate_of = original.item_id
            item.duplicate_links.add(original.item_id)
            original.duplicate_links.add(item.item_id)
            duplicates.append((original, item))
        else:
            seen[key] = item
    return duplicates


def record_conflict(left: ResearchItem, right: ResearchItem, reason: str) -> None:
    left.conflicts.add(right.item_id)
    right.conflicts.add(left.item_id)
    left.history.append(f"conflict:{right.item_id}:{reason}")
    right.history.append(f"conflict:{left.item_id}:{reason}")


class ResearchPipeline:
    """Architecture-only pipeline that stops at KnowledgeCandidate."""

    stages = (
        PipelineStage.DISCOVERY,
        PipelineStage.COLLECTION,
        PipelineStage.CLASSIFICATION,
        PipelineStage.SOURCE_VERIFICATION,
        PipelineStage.DUPLICATE_DETECTION,
        PipelineStage.NORMALIZATION,
        PipelineStage.CONFIDENCE_EVALUATION,
        PipelineStage.KNOWLEDGE_CANDIDATE,
    )

    def process(self, item: ResearchItem) -> KnowledgeCandidate:
        validate_discovery(item)
        item.trust_level = item.source.effective_trust_level()
        item.freshness = evaluate_freshness(item.publication_date)
        normalize_item(item)
        score_item(item)
        item.history.append("knowledge_candidate_created")
        return KnowledgeCandidate(research_item=item)
