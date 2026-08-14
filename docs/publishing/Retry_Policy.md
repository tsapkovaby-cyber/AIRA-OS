# Retry Policy

Network, rate-limit, and transient platform failures are recoverable. Validation,
authentication, media, and permission failures are not. Exponential backoff
starts at 30 seconds with at most three attempts. Exhaustion marks the
publication failed and emits an incident-bearing audit event. Idempotency is
checked before every attempt so ambiguous responses cannot create duplicates.
