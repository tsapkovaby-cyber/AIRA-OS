from datetime import datetime, timezone
import pytest
from backend.retrieval.chunking import chunk_document
from backend.retrieval.embeddings import MockEmbeddingProvider
from backend.retrieval.engine import RetrievalEngine, normalize_query
from backend.retrieval.models import *

def result(id="R1", text="Knowledge graph records architecture decisions", **kw):
    defaults=dict(result_id=id,source_type="docs",source_id=f"S-{id}",title="Architecture",
        summary="Verified architecture evidence",relevant_passage=text,domain=Domain.PROJECT,
        evidence_references=[EvidenceReference(f"S-{id}","Architecture#decisions")])
    defaults.update(kw); return RetrievalResult(**defaults)

def test_normalization_and_domain_selection():
    assert normalize_query("  WHY, Knowledge   Graph? ")=="why knowledge graph"
    assert Domain.DECISIONS in RetrievalEngine.select_domains("why did we decide")

def test_keyword_semantic_ranking_and_provenance():
    engine=RetrievalEngine(); engine.index(result())
    package=engine.search(RetrievalQuery("architecture decisions", "agent", domains={Domain.PROJECT}))
    assert package.selected_sources[0].keyword_score>0
    assert package.selected_sources[0].semantic_score>0
    assert "S-R1" in package.context and package.trace.selected_reasons

def test_permission_filtering_cache_isolation_and_secret_exclusion():
    engine=RetrievalEngine(); engine.index(result(security_classification=SecurityScope.FOUNDER_PRIVATE))
    denied=engine.search(RetrievalQuery("knowledge graph", "content-agent",domains={Domain.PROJECT}))
    assert not denied.selected_sources and "permission denied" in denied.trace.excluded["R1"]
    allowed=engine.search(RetrievalQuery("knowledge graph", "founder",domains={Domain.PROJECT}))
    assert allowed.selected_sources and not allowed.trace.cache_hit
    with pytest.raises(ValueError): engine.index(result("secret",security_classification=SecurityScope.SYSTEM_SECRET))

def test_freshness_confidence_and_historical_retrieval():
    engine=RetrievalEngine()
    old=result("old",confidence=.2,freshness_status=FreshnessStatus.HISTORICAL,
        valid_from=datetime(2025,1,1,tzinfo=timezone.utc)); engine.index(old)
    assert not engine.search(RetrievalQuery("knowledge graph","founder",domains={Domain.PROJECT}),min_confidence=.5).selected_sources
    query=RetrievalQuery("knowledge graph","founder",domains={Domain.PROJECT},freshness_requirement=FreshnessStatus.HISTORICAL)
    assert engine.search(query).selected_sources[0].result_id=="old"

def test_duplicate_conflict_and_context_budget():
    engine=RetrievalEngine()
    engine.index(result("a","Tool X costs ten",metadata={"claim_key":"price","claim_value":10}))
    engine.index(result("b","Tool X costs twenty",metadata={"claim_key":"price","claim_value":20}))
    engine.index(result("dup","Tool X costs ten",source_id="other"))
    package=engine.search(RetrievalQuery("Tool X costs","founder",domains={Domain.PROJECT}))
    assert len(package.selected_sources)==2 and package.conflicts
    context,tokens=engine.build_context(package.selected_sources,package.conflicts,token_budget=30)
    assert tokens<=30

def test_chunking_and_embedding_interface():
    chunks=chunk_document("D1","# First\nUseful coherent paragraph.\n# Second\nMore evidence.")
    assert len(chunks)==2 and chunks[0].section=="First" and chunks[0].hash
    provider=MockEmbeddingProvider(); assert provider.health_check()
    assert len(provider.embed_batch(["a","b"]))==2 and provider.estimate_cost(["a"])==0

def test_missing_knowledge_never_fabricates():
    package=RetrievalEngine().search(RetrievalQuery("unknown verified fact","agent"))
    assert package.missing_information is MissingStatus.INSUFFICIENT_KNOWLEDGE
    assert package.suggested_next_action=="Research" and not package.context

def test_exact_and_related_security():
    engine=RetrievalEngine(); parent=result("p",relationships=["private"])
    private=result("private",security_classification=SecurityScope.FOUNDER_PRIVATE)
    engine.index(parent); engine.index(private)
    agent=RetrievalQuery("x","agent")
    assert engine.retrieve_by_id("private",agent) is None
    assert engine.retrieve_related("p",agent)==[]
