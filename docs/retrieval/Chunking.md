# Chunking

The development chunker preserves Markdown heading, document ID, version, absolute offsets,
content hash, metadata, and security scope. Long sections are bounded at a configurable size.
Content/model/chunking version or material security metadata changes require re-embedding.
`SYSTEM_SECRET` input is rejected before chunks can reach an embedding provider.

