# Publishing Engine

The Publishing Engine is the sole controlled gateway to external platforms. It
accepts only a specific content version approved by both Guardian and Founder,
then queues, preflights, publishes through an adapter, and creates an immutable
receipt. Sprint 011 contains only a non-production mock adapter.

## Boundaries

The engine has execution authority, not editorial authority. It cannot create,
rewrite, approve, or select content and it never receives raw credentials.
Internal timestamps are UTC while a request retains its timezone and local
display time. Analytics and memory receive events; neither concern is
implemented here.
