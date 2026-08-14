# AIRA OS — Integrated Sprints 001–024 Status

## Branch

Canonical staging branch: `integration/sprints-001-024`.

`main` remains the production baseline and the Railway Telegram runtime is not switched to the staging architecture by this integration work.

## Integrated architecture

The staging branch now contains the historical Sprint 001–024 architecture reconciled onto one line of development, including Core boundaries, Knowledge/Memory/Research, Planner/Workflow/Guardian, Content/Publishing, Agents, Founder Dashboard, Intelligence, Retrieval/RAG, Experiments, Digital Human (Visual/Voice/Video), Multimodal Perception, AIRA Academy and Live Language Classroom.

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

## Test discovery

Integrated pytest discovery covers `tests`, `backend`, and `src` so nested subsystem tests are no longer silently excluded.

A full executable regression run has not yet been performed from this integration session because the available execution environment cannot reach GitHub/package registries. Before promotion, run at minimum:

```bash
python -m compileall -q backend src tests
python -m pytest -q
npm ci
npm test
npm run build
```

## Promotion blockers

The staging branch must not be merged to production until all of the following are resolved:

1. Full Python regression suite passes under the supported Python runtime.
2. Founder Dashboard dependencies install and the production build/tests pass.
3. Telegram architecture is consolidated to one future gateway and one running bot process.
4. Environment/config requirements for every activated subsystem are documented and validated.
5. External provider adapters remain disabled unless credentials, budgets, permissions and Guardian/Founder gates are explicitly configured.
6. End-to-end checks verify that publishing, approvals, deletion/privacy controls and emergency pause behavior preserve the intended authority boundaries.

## Pull request cleanup

Historical implementation PRs that were manually reconciled have been closed as superseded. Duplicate/obsolete PRs were closed without merging. The Railway OpenAI/httpx compatibility fix remains part of `main` and is also present in the staging ancestry.

## Current state

Sprints 001–024 are structurally assembled in staging. The next phase is cross-subsystem regression, import/dependency cleanup, Telegram convergence, and promotion-readiness review — not production activation.
