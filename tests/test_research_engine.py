from datetime import date, timedelta

import pytest

from aira_os.research_engine import ResearchAPI, ResearchPipeline
from aira_os.research_engine.models import (
    Freshness,
    InformationCategory,
    PipelineStage,
    ResearchItem,
    SecurityContext,
    Source,
    SourceCategory,
    TrustLevel,
)
from aira_os.research_engine.services import (
    ResearchValidationError,
    calculate_confidence,
    detect_duplicates,
    evaluate_freshness,
    normalize_item,
    record_conflict,
    validate_discovery,
)


def make_item(title="New Model Release", source_url="https://example.com/release"):
    return ResearchItem(
        title=title,
        summary=" Official release notes describe an AI model update. ",
        source=Source("Example", source_url, SourceCategory.OFFICIAL, verified=True),
        author="Example Team",
        publication_date=date.today(),
        language="en",
        category=InformationCategory.AI_MODELS,
        tags={" AI Models ", "Release"},
        security=SecurityContext(owner="research", visibility="internal", permissions=("read",)),
    )


def test_research_engine_initializes_successfully():
    api = ResearchAPI()
    assert isinstance(api.pipeline, ResearchPipeline)


def test_discovery_validation_requires_metadata():
    item = make_item()
    item.title = ""
    with pytest.raises(ResearchValidationError):
        validate_discovery(item)


def test_classification_assigns_level_a_for_official_source():
    item = make_item()
    assert item.trust_level == TrustLevel.LEVEL_A


def test_normalization_cleans_title_summary_and_tags():
    item = make_item(title="  New   Model   Release  ")
    normalize_item(item)
    assert item.title == "New Model Release"
    assert "ai-models" in item.tags
    assert "normalized" in item.history


def test_confidence_calculation_uses_trust_and_verification():
    item = make_item()
    confidence = calculate_confidence(item)
    assert confidence == pytest.approx(0.95)


def test_duplicate_detection_links_and_preserves_duplicates():
    first = make_item()
    second = make_item(title="  new model release  ", source_url="https://example.com/release/")
    duplicates = detect_duplicates([first, second])
    assert duplicates == [(first, second)]
    assert second.duplicate_of == first.item_id
    assert first.item_id in second.duplicate_links
    assert second.item_id in first.duplicate_links


def test_conflict_handling_records_both_sides_without_resolution():
    first = make_item(title="Benchmark Result A")
    second = make_item(title="Benchmark Result B", source_url="https://example.com/other")
    record_conflict(first, second, "trusted sources disagree")
    assert second.item_id in first.conflicts
    assert first.item_id in second.conflicts
    assert any("trusted sources disagree" in entry for entry in first.history)


def test_search_finds_items_by_tag():
    api = ResearchAPI()
    item = api.create_item(make_item())
    results = api.search("release")
    assert item in results


def test_pipeline_returns_knowledge_candidate_and_never_publishes():
    candidate = ResearchPipeline().process(make_item())
    assert candidate.pipeline_stage == PipelineStage.KNOWLEDGE_CANDIDATE
    assert candidate.research_item.score is not None
    assert "knowledge_candidate_created" in candidate.research_item.history


def test_freshness_categories():
    today = date(2026, 7, 15)
    assert evaluate_freshness(today - timedelta(days=3), today) == Freshness.FRESH
    assert evaluate_freshness(today - timedelta(days=20), today) == Freshness.RECENT
    assert evaluate_freshness(today - timedelta(days=90), today) == Freshness.CURRENT
    assert evaluate_freshness(today - timedelta(days=500), today) == Freshness.OLD
    assert evaluate_freshness(today - timedelta(days=900), today) == Freshness.HISTORICAL
