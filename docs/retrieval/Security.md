# Security

Public and internal evidence is available to ordinary internal agents. Founder-private evidence
requires the Founder requester or an explicit task-scoped permission. It uses a security-sensitive
cache key, so privileged results cannot serve an unprivileged request. `SYSTEM_SECRET` is neither
a retrieval domain nor an allowed scope and is rejected from record, chunk, and vector indexes.
Traces may note a denied result ID but never include its passage or sensitive query contents in logs.

