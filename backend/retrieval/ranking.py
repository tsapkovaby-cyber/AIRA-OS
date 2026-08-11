"""Configurable hybrid evidence scoring and diversity-aware deduplication."""
from dataclasses import dataclass
from .models import RetrievalResult

@dataclass(frozen=True)
class RankingWeights:
    keyword: float=.28; semantic: float=.28; graph: float=.08; freshness: float=.12
    confidence: float=.10; importance: float=.06; source_trust: float=.08

def rank(results: list[RetrievalResult], weights=RankingWeights()) -> list[RetrievalResult]:
    for item in results:
        item.score = sum((item.keyword_score*weights.keyword, item.semantic_score*weights.semantic,
                          item.graph_score*weights.graph, item.freshness*weights.freshness,
                          item.confidence*weights.confidence, item.importance*weights.importance,
                          item.source_trust*weights.source_trust))
    return sorted(results, key=lambda x: x.score, reverse=True)

def deduplicate(results: list[RetrievalResult]) -> list[RetrievalResult]:
    unique, seen = [], set()
    for item in results:
        key = item.metadata.get("text_hash") or " ".join(item.relevant_passage.casefold().split())
        if key in seen: continue
        seen.add(key); unique.append(item)
    return unique
