# Sprint 015 Report

## Summary

Implemented the provider-independent intelligence domain, router, execution service, safe context construction, prompt version hashing, validation, health, budgets, audit, fallback, mock provider, and adapter skeletons.

## Provider Architecture and Providers Added

`IntelligenceProvider` is the sole inference boundary. A full mock simulates success, malformed/empty output, timeout, rate limiting, outage, and latency. OpenAI, Anthropic, Gemini, and local adapter skeletons intentionally require later transport and Secret Provider wiring.

## Model Profiles, Task Profiles, and Routing Logic

Profiles describe capabilities, limits, price, latency, reliability, sensitivity, status, evaluations, and fallback IDs. Ten reusable task profiles are supplied. Hard constraints filter candidates before policy scoring; agents cannot name an arbitrary model.

## Fallback Logic

Only compatible configured fallbacks are retained. Timeouts, rate limits, outages, content/unknown errors, and invalid structured responses may fall back. Policy and permission failures never reach a provider.

## Cost Controls

Token-based estimates support routing and preflight budget authorization. Accepted costs are recorded. Durable daily/monthly aggregation and reserved safety budgets remain technical debt.

## Security Controls and Prompt Integration

The context builder removes system secrets, gates Founder-private data, budgets context, and preserves instruction/data roles. Prompt registry resolution records exact versions and SHA-256 hashes. Audit records contain no credentials. Tool execution is explicitly outside provider authority.

## Tests and Test Results

Tests cover registration, validation, capability routing, fallback failure modes, cost/budget blocking, disablement, health, structured output, sensitivity, injection separation, prompt hashing, audit safety, agent restrictions, and explainability. The full test suite passes locally.

## Known Limitations and Technical Debt

Production transports, persistent audit/budget storage, circuit-breaker state transitions, schema vocabulary beyond the dependency-free subset, retries, streaming safety buffering, tool-runtime integration, dashboard controls, and durable event-bus publication are not yet wired. No paid API is required.

## Recommendations for Sprint 016

Before activating production providers, connect Secret Provider and persistent stores, implement an event-bus-backed circuit breaker, add full JSON Schema validation, and run controlled provider evaluations. Do not roll out critical profiles without regression thresholds and Founder approval.
