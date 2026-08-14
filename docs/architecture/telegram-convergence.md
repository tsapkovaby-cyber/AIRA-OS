# Telegram convergence plan

## Decision

AIRA OS will keep exactly one Telegram process.

The existing `backend/integrations/telegram` python-telegram-bot entry point remains the only deployable transport while convergence is staged. The transport-neutral contracts in `backend/telegram` are the canonical future Telegram/Core boundary. The later `src/aira_os/telegram` implementation is retained as a source of hardened capabilities (webhook ingestion, persistence, media handling, approvals, pause/resume, rate limiting and audit), but it must not be started as another bot runtime.

## Current migration seam

`backend/integrations/telegram/core_bridge.py` converts a live Telegram message into the canonical `FounderMessage` and `FounderIdentity` models.

`TelegramGateway` accepts an optional `AiraCoreGateway`. When absent, it uses the existing `AIRAConversationService` exactly as the Railway MVP does today. When supplied in staging/tests, ordinary Founder chat is routed through the canonical Core port. Local transport commands remain local during this phase.

The production `build_application()` does not supply a Core gateway yet, so this change cannot activate a second architecture or change Railway behavior by itself.

## Migration order

1. Keep authentication, `/start`, `/help`, `/privacy`, `/delete_my_data` and `/health` on the current transport boundary.
2. Route ordinary text through the canonical `AiraCoreGateway` behind an explicit runtime composition step.
3. Move approval callbacks and signed callback verification behind the same gateway.
4. Adapt Perception/voice/media handling without creating a second polling/webhook consumer.
5. Adapt persistent session/memory storage and preserve per-Founder deletion semantics.
6. Move pause/resume and workflow/research commands behind Core authority checks.
7. Only after equivalent regression coverage, remove duplicate runtime code from `src/aira_os/telegram`; retain reusable domain/security components as appropriate.

## Invariants

- One bot token, one active Telegram update consumer.
- Founder authorization occurs before Core actions.
- External side effects remain approval-gated.
- Provider errors and secrets are never returned to Telegram users or logged verbatim.
- `/delete_my_data` must clear every AIRA-owned store that has been activated for that user.
- Webhook secrets are required only in webhook mode; polling must not depend on them.
- Staging adapters are opt-in and cannot silently change the Railway entry point.
