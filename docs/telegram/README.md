# Founder Telegram gateway

The Telegram integration is a private **interface**, not an intelligence layer.
It authenticates the Founder, normalizes transport data, validates callbacks and
delegates messages and actions through the `AiraCoreGateway` port. AIRA Core owns
intent detection, planning, workflows, Guardian checks, approvals, publishing,
memory and all durable business state.

## Configuration

Infrastructure must inject these values through a secret provider:

- Telegram bot token (used only by the Telegram client);
- at least 32 random bytes for callback signing;
- immutable Telegram user ID to Founder identity mappings and permissions.

Tokens and callback secrets must never be logged or committed. Production should
use webhooks; development may supply updates through polling to the same
`TelegramBotService.receive` method.

## Package map

- `adapter/`: update normalization and response delivery only;
- `application/`: authentication/guard orchestration and Core ports;
- `auth/`: immutable-ID allowlist and permission checks;
- `callbacks/`: signed, expiring references;
- `messaging/`: idempotency and per-user throttling;
- `schemas/`: transport-neutral records;
- `tests/`: security-boundary and delivery tests.

The included stores are deterministic in-process MVP implementations. Deployments
with multiple replicas must bind equivalent shared, atomic TTL stores (for example,
Redis) so replay protection and throttling work across replicas and restarts.
