# Intelligence Provider Layer

Sprint 015 establishes a provider-independent boundary for bounded inference. AIRA identity remains in the Constitution, prompt registry, core, memory, knowledge, and decision systems—not in a model adapter.

## Components

- `IntelligenceProvider` normalizes generation, structured responses, streaming, health, capabilities, and cost.
- `ModelRouter` filters by capability, context, sensitivity, reliability, health, latency, and budget before applying policy.
- `IntelligenceService` executes an auditable fallback chain and records every attempt.
- `ContextBuilder` enforces context budgets and excludes system secrets and unauthorized Founder-private data.
- `PromptRegistry` resolves immutable prompt versions and SHA-256 hashes.
- `MockIntelligenceProvider` supports credential-free development and deterministic failure testing.

Real provider classes are deliberately inert adapter skeletons. Credentials must be supplied by a future Secret Provider, never source configuration.

