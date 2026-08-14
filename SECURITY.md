# Security Policy

AIRA OS must not store production secrets, API keys, bot tokens, private voice references, or private user data in the public repository.

## Reporting

If a secret is exposed, revoke or rotate it immediately before continuing development. Security-sensitive changes should be reviewed before merge.

## Repository rules

- Keep runtime secrets in deployment environment variables.
- Keep `.env` files untracked.
- Avoid logging credentials or full authorization headers.
- Treat Telegram, AI-provider, media, and user-supplied content as untrusted input.
- Preserve Founder approval gates for sensitive or public actions.
