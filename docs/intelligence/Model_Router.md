# Model Router

Routing first rejects disabled, unhealthy, insufficient-capability, undersized-context, unreliable, sensitivity-incompatible, slow, or over-task-cost profiles. Policies then order valid candidates by quality, cost, latency, or an explicitly permitted Founder preference. `explain_routing()` returns requirements, selected profile, alternatives, estimated cost, rationale, and fallbacks.

