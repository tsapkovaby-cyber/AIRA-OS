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

## Telegram boundaries

Three Telegram-related layers currently exist for different historical purposes:

1. `backend/integrations/telegram` — current production/MVP transport lineage.
2. `backend/telegram` — secure Founder gateway architecture retained for reconciliation.
3. `src/aira_os/telegram` — later webhook/gateway/worker architecture retained for reconciliation.

Only the existing production transport is considered deployable today. The other two are staging architectures and must not be started as additional bot processes. Final consolidation must select one future gateway contract and migrate the production adapter behind it before enabling it.

### Telegram configuration convergence completed in this audit

Sprint 022 originally required `TELEGRAM_WEBHOOK_SECRET` even when using long polling and used the string `long_polling`, while the live MVP uses `polling`. The staging `src/aira_os/telegram/config.py` now:

- requires webhook secret only in webhook mode;
- accepts both `polling` and `long_polling` and normalizes them to one internal mode;
- keeps `TELEGRAM_BOT_TOKEN` and `AIRA_FOUNDER_TELEGRAM_ID` mandatory;
- has regression tests covering polling/webhook behavior.

This removes an environment-contract conflict before any future Telegram convergence work.

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

## Continuous regression gates

Two staging GitHub Actions workflows are now committed:

- `.github/workflows/integration-python.yml`
- `.github/workflows/integration-dashboard.yml`

They run automatically on pushes to `integration/sprints-001-024` and on pull requests targeting `main`.

### Python regression result

Python 3.11 CI successfully:

- installed `requirements.txt` and the editable project dev dependencies;
- compiled `backend`, `src`, `aira_memory`, and `tests`;
- ran the consolidated test discovery across `tests`, `backend`, and `src`;
- passed **249 tests** after the Telegram configuration convergence tests were added.

This confirms the previously separate Python sprint test suites can currently coexist under one Python 3.11 environment with the production OpenAI/httpx/Telegram dependency pins.

### Founder Dashboard regression result

Node.js CI successfully:

- installed Dashboard dependencies;
- ran the Vitest suite;
- completed `next build` with CI-only placeholder environment values for the Dashboard credential contract.

The Dashboard therefore compiles as part of the consolidated staging repository without requiring production secrets.

## Remaining promotion blockers

The staging branch must not be merged to production until all of the following are resolved:

1. Telegram architecture is consolidated to one future gateway contract and one running bot process.
2. Environment/config requirements for every subsystem selected for activation are documented and validated.
3. External provider adapters remain disabled unless credentials, budgets, permissions and Guardian/Founder gates are explicitly configured.
4. End-to-end checks verify publishing, approvals, deletion/privacy controls and emergency pause behavior across the selected production composition.
5. A production migration plan defines which staging modules are activated immediately and which remain dormant libraries.
6. Dashboard dependency reproducibility should be improved with a committed npm lockfile before production deployment.

## Pull request cleanup

Historical implementation PRs that were manually reconciled have been closed as superseded. Duplicate/obsolete PRs were closed without merging. The Railway OpenAI/httpx compatibility fix remains part of `main` and is also present in the staging ancestry.

## Current state

Sprints 001–024 are structurally assembled and the first full cross-sprint regression gate is green. The next active assembly phase is Telegram convergence and production-composition design, followed by end-to-end authority/privacy tests and a promotion-readiness PR. No production activation has occurred.
