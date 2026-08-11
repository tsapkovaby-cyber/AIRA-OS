# AIRA Telegram MVP v0.1 — implementation report

## Scope and files

Sprint 022 integration milestone only; Sprint 025 was not implemented. Added the Telegram package (`bot.py`, `gateway.py`, `handlers.py`, `auth.py`, `config.py`, `conversation.py`, `intelligence.py`, and package initializers), environment templates/ignore rules, dependency manifests, tests, and operator documentation.

## Architecture

The implemented call path is:

`Telegram update → TelegramGateway → AIRAConversationService → AIRAIntelligenceProvider → OpenAI Responses API`

The handler is only a Telegram transport adapter. The gateway authenticates by numeric user ID, dispatches commands, sanitizes errors, and records operational metadata. `AIRAConversationService` owns conversational flow. Its replaceable `ConversationStore` interface currently uses a bounded in-process store keyed by `(Telegram user ID, chat ID)`. Provider calls are centralized in `OpenAIResponsesProvider`; canonical AIRA identity, mission, approval constraint, and disclaimer instructions are passed as Responses API system instructions.

Polling and webhook startup are mutually exclusive configuration modes. `/health` reports only boolean readiness, never configuration values.

## Tests

Automated coverage includes `/start`, Founder numeric-ID authentication, denial and isolation for unknown users, Russian conversational response, canonical AI identity, contextual memory and chat isolation, `/privacy`, local `/delete_my_data`, setup-only ID discovery, provider failure sanitization, Telegram delivery failure, health output, and secret non-disclosure.

Run with `pytest -q` after installing `requirements-dev.txt`.

## Configuration still required

Deployment must provide secrets outside Git:

- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`
- `AIRA_FOUNDER_TELEGRAM_ID` (numeric)

Optional configuration: `AIRA_MODEL`, `PRIVACY_POLICY_URL`, and webhook variables documented in `README_TELEGRAM_MVP.md`. The repository contains no operational credentials.

## Deployment

Follow `README_TELEGRAM_MVP.md`. Use polling for a single development process. For production set webhook mode, an HTTPS webhook URL, and port, ensure no polling process is active, then run the same Python module under the cloud process supervisor.

## Known limitations

- Conversation memory is bounded and process-local; restarts clear it and horizontally scaled workers do not share it.
- Only the configured Founder can converse in this private MVP; public users receive denial.
- Local deletion cannot assert deletion of data retained independently by Telegram or OpenAI.
- Health is a configuration/readiness response, not a live upstream connectivity probe.
- No external/public actions or Academy/language subsystems were added.
