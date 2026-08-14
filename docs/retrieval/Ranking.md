# Ranking

Hybrid scores combine keyword and semantic relevance, graph proximity, freshness, confidence,
importance, and source trust. Weights are immutable configuration values and no signal exceeds
28% by default. Exact duplicate passages or hashes are removed after ranking; source diversity
therefore does not spend context on repeated text. Contradictory values for a shared `claim_key`
produce an explicit unresolved conflict rather than being silently merged.

