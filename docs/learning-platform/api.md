# Learning Platform API — Sprint 027

`backend.learning_api.LearningPlatformAPI` is the authenticated, transport-neutral boundary for future web/mobile transports. It composes Sprint 026 `AccountService` with Sprint 025 `LearningPlatformService` and never trusts a client-supplied student ID.

Supported MVP operations: registration, login/logout, current account resolution, learning profile read/update, course catalog, enrollment, course progress, next/start/complete lesson, and tutor-session start.

Every student-scoped operation derives the Student from the authenticated account session. This prevents horizontal access to another learner by changing a request student identifier.

The facade deliberately does not depend on FastAPI, Railway, Telegram, OpenAI, cookies, CORS, or a database. A later HTTP adapter can translate HTTP requests/responses into these operations while keeping authentication and learning rules in their canonical domains.

Session tokens remain opaque credentials owned by the accounts domain. Production HTTP adapters must transmit them only over TLS and should prefer secure HttpOnly cookies for browser sessions, with CSRF protection where cookie authentication is used.
