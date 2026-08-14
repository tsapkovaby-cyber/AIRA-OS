# Prompt Registry

Prompts are immutable versioned definitions containing prompt ID, agent type, version, content reference, status, timestamps, and approval. The registry resolves a requested approved version or latest approved semantic version. Agent registration and startup validation fail when an approved prompt reference is missing.

Prompt content lives behind references rather than application constants. External documents are untrusted data, never system instructions; pages cannot add tools. Prompt changes require a new version, review, and controlled agent rollout.
