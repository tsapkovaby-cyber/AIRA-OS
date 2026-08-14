# Platform Adapters

Adapters validate platform constraints, prepare an approved snapshot, publish
with an idempotency key, and expose health. Optional schedule, delete, status,
lookup, credential refresh, and health operations must fail explicitly when
unsupported. The mock simulates success, network error, rate limit,
authentication error, platform rejection, timeout, and duplicate request.

Telegram, Instagram, TikTok, YouTube, MAX, Website, and Newsletter integrations
are deferred. No undocumented capability or real account is connected.
