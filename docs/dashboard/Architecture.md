# Dashboard Architecture

The Next.js App Router application is split into presentation components, typed view data, middleware authentication, and server route handlers. Pages do not access a database. Production adapters should replace demonstration route data by calling existing AIRA service APIs (`/system`, `/approvals`, `/agents`, `/research`, `/knowledge`, `/memory`, `/content`, `/workflows`, `/publishing`, `/incidents`, `/costs`, and `/audit`).

The server remains the source of truth. Mutations require a current session, CSRF proof, validated payload, current object version, role check, and service-side audit. Structured errors contain a stable code and reference ID. Polling can later be replaced by SSE without changing view contracts.
