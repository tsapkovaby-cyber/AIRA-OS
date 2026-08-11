# Provider Interface

Adapters implement `generate`, `generate_structured`, `stream`, `health_check`, `estimate_cost`, and `get_capabilities`. Errors normalize to timeout, rate-limit, authentication, bad-request, unavailable, content, and unknown categories. OpenAI, Anthropic, Gemini, and local names currently point to inert skeleton adapters; automated tests use only the mock.

