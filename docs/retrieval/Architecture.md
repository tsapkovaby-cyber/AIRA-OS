# Architecture

The pipeline is normalize → domain selection → authorization → plan → keyword/vector candidate
generation → metadata filtering → hybrid ranking → deduplication → conflict detection → context.
Authorization predicates are applied before candidate material enters lexical or semantic search.

`EmbeddingProvider` and `VectorStore` are ports. `MockEmbeddingProvider` and
`InMemoryVectorStore` are deterministic development adapters; pgvector or Qdrant adapters can be
added without changing domain logic. Graph mode is planned when a why/relationship query is seen,
but an external graph adapter is future work.

