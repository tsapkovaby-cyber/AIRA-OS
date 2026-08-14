# Sprint 016 Report — Retrieval & RAG Engine

## Summary

Implemented a functional local RAG path that returns grounded, provenance-bearing packages and an
explicit `INSUFFICIENT_KNOWLEDGE` result rather than fabricating internal evidence.

## Retrieval Architecture

Typed queries, results, packages, traces, conflicts, chunks, and vector records form the domain.
The orchestrator separates planning, authorization, candidate generation, filtering, ranking,
deduplication, conflict detection, caching, context construction, and minimal query telemetry.

## Search Modes

The MVP performs keyword and semantic retrieval with hybrid fusion. It recognizes time-aware and
graph-relevant plans, provides exact-ID, related-record, and historical APIs, and keeps graph store
integration as a bounded future adapter.

## Ranking Strategy

Configurable weights combine keyword, semantic, graph, freshness, confidence, importance, and
source trust. Duplicate passages are eliminated and current/high-quality evidence naturally ranks
above stale or weak evidence. Conflicts remain separate objects.

## Security Model

Permission filtering occurs before candidate ranking. Founder-private access requires identity or
task delegation; cache keys include permissions. Secret records are rejected at every indexing
entry point and secret scope can never be requested through RAG.

## Embedding Layer

`EmbeddingProvider` defines single/batch embedding, health, and cost operations. The deterministic
hash-based mock makes tests offline and repeatable and is explicitly not a production model.

## Vector Store

`VectorStore` defines upsert, scoped similarity search, and deletion. The in-memory implementation
provides safe development behavior while leaving pgvector/Qdrant adapters replaceable.

## Context Builder Integration

Evidence is emitted as bounded context blocks retaining source, version, confidence, freshness,
and contradictions. The Sprint 015 outer builder can place it beneath policy and task instructions.

## Tests and Test Results

Unit tests exercise required MVP behavior and negative security guarantees. The full repository
test suite passes locally with no network service or external model dependency.

## Known Limitations

- No production graph, vector database, or provider adapter.
- Hash embeddings demonstrate the interface but have limited semantic quality.
- Chunk overflow currently skips whole evidence rather than performing generative compression.
- Domain adapters are represented by typed `source_type` records rather than live prior-sprint stores.
- Query logging is in memory and metrics aggregation is not yet exported.

## Technical Debt

Persist audit/metrics events, add stable repository indexing checkpoints, improve near-duplicate
detection, add claim extraction, and integrate Sprint 015 model-router enforcement against invented
source IDs.

## Recommendations for Sprint 017

Do not begin Sprint 017 without Founder approval. When approved, prioritize real subsystem adapters,
production vector-store conformance tests, graph fusion, offline quality fixtures, and context
compression that preserves counter-evidence.
