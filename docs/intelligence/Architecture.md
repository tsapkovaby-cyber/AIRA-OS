# Architecture

Agents submit task-profile IDs rather than model IDs. The router selects a healthy compatible model; the service invokes its adapter and validates the result. Retryable transport or validation failure advances only to a capability-compatible fallback. Provider adapters own authentication, wire formats, usage extraction, and error mapping, but no AIRA business or identity rules.

Events captured by the audit log include `InferenceRequested`, `ModelRouted`, `InferenceStarted`, `InferenceCompleted`, `InferenceFailed`, and `FallbackTriggered`. Audit data contains identifiers and metadata, never credentials.

