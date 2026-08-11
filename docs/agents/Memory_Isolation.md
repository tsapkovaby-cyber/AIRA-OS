# Memory Isolation

Scopes are `NONE`, `TASK_ONLY`, `AGENT_PRIVATE`, `PROJECT_SHARED`, `KNOWLEDGE_READ`, `KNOWLEDGE_WRITE`, `FOUNDER_PRIVATE`, and `SYSTEM_PRIVATE`. Scope is explicit; `NONE` cannot be combined. The authorizer rejects any scope absent from the manifest.

Context builders should retrieve only task-relevant references. Research receives task/research/selected knowledge, while Founder-private conversations, credentials, and unrelated business secrets remain excluded.
