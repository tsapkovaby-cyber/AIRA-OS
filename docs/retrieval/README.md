# Retrieval & RAG Engine

Sprint 016 provides a dependency-free, permission-aware retrieval path. Callers submit a
`RetrievalQuery` to `RetrievalEngine.search()` and receive a `RetrievalPackage` containing
ranked evidence, provenance, conflicts, missing-knowledge state, bounded context, and trace.

The MVP indexes approved structured records and documentation chunks. It deliberately rejects
`SYSTEM_SECRET`; raw conversations are not automatically considered durable memory.

## API

The engine exposes `search`, `retrieve`, `retrieve_by_id`, `retrieve_related`,
`retrieve_history`, `retrieve_conflicts`, `build_context`, and `explain_retrieval`.

