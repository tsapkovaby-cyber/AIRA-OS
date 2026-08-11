# Security

- Authenticate only immutable Telegram user IDs; never usernames/display names.
- Deny unknown users without returning project information.
- Fetch bot tokens and signing material from a secret provider and redact logs.
- Sign every callback with HMAC, expire it, authorize its action, claim its update
  ID and revalidate the referenced object in Core.
- Apply per-user ingress limits even to a private bot.
- Require second confirmation (and optional secondary PIN at the Core policy
  boundary) for publication, agent disabling, pause and emergency stop.
- Use TLS webhook verification at ingress and rotate webhook/signing secrets.
- Keep Founder conversations `FOUNDER_PRIVATE` unless an explicit memory policy
  grants another principal access.

The in-process replay and rate stores are suitable for one development process.
Production requires atomic shared storage with retention and monitoring.
