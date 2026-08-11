# Tool Access

Every tool has an ID, category, risk level, allowed agent types, required permissions, rate limit, and audit policy. Universal access does not exist. Unknown tools fail closed. Each execution logs the declared tools, provider, task, workflow, and agent version.

Adapters should encapsulate secrets: an agent asks a registered adapter to perform an authorized operation and never receives raw tokens. Network and filesystem access default to denied. Production external adapters are outside Sprint 012.
