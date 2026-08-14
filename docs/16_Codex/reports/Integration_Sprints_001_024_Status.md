# AIRA OS — Integrated Sprints 001–024 Status

## Branch

Canonical staging branch: `integration/sprints-001-024`.

`main` remains the production baseline and the Railway Telegram runtime is not switched to the staging architecture by this integration work.

## Integrated architecture

The staging branch contains the historical Sprint 001–024 architecture reconciled onto one line of development, including Core boundaries, Knowledge/Memory/Research, Planner/Workflow/Guardian, Content/Publishing, Agents, Founder Dashboard, Intelligence, Retrieval/RAG, Experiments, Digital Human (Visual/Voice/Video), Multimodal Perception, AIRA Academy and Live Language Classroom.

## Canonical package decisions

- Workflow Engine: `src/aira_os/workflow_engine`.
- Guardian Engine: `src/aira_os/guardian_engine`.
- Perception: `src/aira_os/perception`.
- AIRA Academy: `backend/education`.
- Live Classroom: `backend/education/live_classroom`.
- Digital Human Visual: `backend/digital_human/visual`.
- Digital Human Voice: `backend/digital_human/voice`.
- Digital Human Video/Motion/Lip-Sync: `backend/digital_human/video`.
- Digital Human root facade remains multimodal and must not be replaced by a modality-specific profile.

## Telegram convergence

Three Telegram-related layers remain in the repository for historical reasons:

1. `backend/integrations/telegram` — the current production/MVP python-telegram-bot transport and the only runtime that may be started today.
2. `backend/telegram` — selected as the canonical future transport-neutral Telegram/Core contract (Founder models, authorization, callback and gateway ports).
3. `src/aira_os/telegram` — retained as a source of later hardened capabilities such as webhook ingestion, persistence, media handling, approvals, pause/resume, rate limiting and audit; it is not a second deployable bot runtime.

The canonical direction is now explicit: keep one Telegram process, migrate the current production transport behind the `backend/telegram` Core gateway contract, and reuse useful Sprint 022 capabilities without starting its worker as another update consumer.

### Core bridge added

`backend/integrations/telegram/core_bridge.py` now converts the live MVP message into canonical `FounderMessage` and `FounderIdentity` objects.

The existing `TelegramGateway` accepts an optional `AiraCoreGateway`. When no Core gateway is supplied, it continues to call the existing `AIRAConversationService` exactly as the current Railway composition does. When a Core gateway is supplied in staging/tests, ordinary Founder chat is routed through the canonical transport-neutral Core port.

The production `build_application()` has not been changed to supply this gateway, so the bridge is an opt-in migration seam and cannot activate a second architecture by itself.

The live handler now also preserves the Telegram `message_id` when available; legacy/mocked messages without that attribute safely fall back to `0`.

### Telegram configuration convergence

Sprint 022 originally required `TELEGRAM_WEBHOOK_SECRET` even when using long polling and used the string `long_polling`, while the live MVP uses `polling`. The staging `src/aira_os/telegram/config.py` now:

- requires webhook secret only in webhook mode;
- accepts both `polling` and `long_polling` and normalizes them to one internal mode;
- keeps `TELEGRAM_BOT_TOKEN` and `AIRA_FOUNDER_TELEGRAM_ID` mandatory;
- has regression tests covering polling/webhook behavior.

The detailed migration sequence and invariants are recorded in `docs/architecture/telegram-convergence.md`.

## Security corrections already applied

- Removed hard-coded Founder Dashboard demo credentials and fixed session token.
- Dashboard authentication now requires environment-provided email/password/session token.
- Replaced fixed Dashboard CSRF value with per-login double-submit CSRF token.
- Logout clears both session and CSRF cookies.
- Dashboard action audit IDs are generated rather than fixed demo values.
- Duplicate Sprint 018 visual implementations were reduced to one canonical visual package.
- Voice and Video were integrated as separate modalities rather than replacing Visual or the multimodal root profile.
- Historical repository-level configuration files were not allowed to overwrite the consolidated baseline during subsystem imports.
- `.env.example` remains value-free and documents the staging Dashboard variables.
- Telegram provider/Core failures remain sanitized at the transport boundary.

## Continuous regression gates

Two staging GitHub Actions workflows are committed:

- `.github/workflows/integration-python.yml`
- `.github/workflows/integration-dashboard.yml`

They run automatically on pushes to `integration/sprints-001-024` and on pull requests targeting `main`.

### Python regression result

Python 3.11 CI successfully:

- installed `requirements.txt` and the editable project dev dependencies;
- compiled `backend`, `src`, `aira_memory`, and `tests`;
- ran the consolidated test discovery across `tests`, `backend`, and `src`;
- passed **253 tests** after the Core bridge regression tests were added.

During this phase CI caught one compatibility regression immediately: the transport handler initially assumed every mocked/effective message exposed `message_id`. That failed an existing error-delivery test; the handler was corrected to use a safe fallback and the next full run returned to green with 253 passing tests.

### Founder Dashboard regression result

Node.js CI successfully:

- installed Dashboard dependencies;
- ran the Vitest suite;
- completed `next build` with CI-only placeholder environment values for the Dashboard credential contract.

The Dashboard continues to compile successfully after the Telegram convergence changes.

## Remaining promotion blockers

The staging branch must not be merged to production until all of the following are resolved:

1. Implement a concrete canonical Core gateway composition and exercise it end-to-end while keeping the legacy Railway composition as the default until cutover approval.
2. Migrate signed approval callbacks and their idempotency/audit path behind the same single Telegram transport.
3. Integrate Perception/media/voice through the selected gateway without introducing a second polling/webhook consumer.
4. Unify activated Memory/session stores and guarantee `/delete_my_data` clears every AIRA-owned store in the production composition.
5. Move pause/resume, workflow and research controls behind Core/Guardian/Founder authority boundaries.
6. Environment/config requirements for every subsystem selected for activation must be documented and validated.
7. External provider adapters remain disabled unless credentials, budgets, permissions and Guardian/Founder gates are explicitly configured.
8. A production migration plan must define which staging modules are activated immediately and which remain dormant libraries.
9. Dashboard dependency reproducibility should be improved with a committed npm lockfile before production deployment.

## Pull request cleanup

Historical implementation PRs that were manually reconciled have been closed as superseded. Duplicate/obsolete PRs were closed without merging. The Railway OpenAI/httpx compatibility fix remains part of `main` and is also present in the staging ancestry.

## Current state

Sprints 001–024 are structurally assembled, Python regression is green at 253 tests, Dashboard regression/build is green, and Telegram convergence has moved from architecture selection to an executable opt-in Core bridge. No production activation or second Telegram process has occurred. The next assembly step is approval/callback convergence and a concrete Core composition for staging end-to-end tests.
