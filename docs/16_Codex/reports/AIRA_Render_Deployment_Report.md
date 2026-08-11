# AIRA Render Deployment Report

## Source and scope

- **Main commit used:** `a4bb82a308e508f6eeff7ce610ae319b6c841d7c` (the locally available merge commit for Telegram MVP v0.1).
- **Branch:** `codex/render-deployment`.
- Scope is limited to Render deployment support, configuration hardening, health support, documentation, and tests. The existing `TelegramGateway`, authentication, OpenAI provider, commands, and process-local conversation service remain in place.

## Files changed

- `render.yaml`
- `.env.example`
- `requirements.txt`
- `README_TELEGRAM_MVP.md`
- `backend/integrations/telegram/bot.py`
- `backend/integrations/telegram/config.py`
- `backend/integrations/telegram/health.py`
- `tests/test_telegram_mvp.py`
- `docs/16_Codex/AIRA_RENDER_DEPLOYMENT_GUIDE.md`
- `docs/16_Codex/reports/AIRA_Render_Deployment_Report.md`

## Render architecture

One Render Python 3.11 web service runs one long-polling process. A small standard-library HTTP server runs alongside polling and returns a secret-free JSON response at `/health`. Render monitors that endpoint and automatically redeploys commits. `numInstances: 1` prevents competing polling instances.

The exact start command is:

```text
python -m backend.integrations.telegram.bot
```

The command targets the existing module entry point. Polling is initial/default delivery. Existing webhook delivery remains available later at the fixed `/telegram` path, requires Telegram's secret-token header, and does not put a token or webhook secret in the URL. Polling and webhook are mutually exclusive.

## Environment variables

Required for normal operation:

- `TELEGRAM_BOT_TOKEN` (secret)
- `OPENAI_API_KEY` (secret)
- `AIRA_FOUNDER_TELEGRAM_ID` (numeric private identifier; intentionally empty only during Stage A)
- `AIRA_MODEL`
- `PRIVACY_POLICY_URL` (may be empty to use the temporary notice)
- `TELEGRAM_DELIVERY_MODE=polling`

Future webhook variables:

- `TELEGRAM_WEBHOOK_URL`
- `TELEGRAM_WEBHOOK_SECRET` (secret)
- `PORT` (provided by Render)

No real values are stored in the repository.

## Founder bootstrap flow

1. Stage A deploys with `AIRA_FOUNDER_TELEGRAM_ID` empty.
2. The Founder privately sends `/start` and receives the sender's numeric Telegram ID.
3. The Founder saves those digits in Render as `AIRA_FOUNDER_TELEGRAM_ID` and redeploys.
4. After configuration, `/start` returns the standard greeting and never reveals the ID. Authentication compares numeric Telegram IDs, never usernames.

## Tests and security checks

- `python -m pytest -q`: 10 passed, 1 skipped. The skipped adapter test uses `pytest.importorskip("telegram")` because runtime dependencies were not installed in the execution environment; no live Telegram integration was claimed.
- `python -m compileall -q backend tests`: passed.
- `git diff --check`: passed.
- `git check-ignore .env` and the tracked-`.env` check: passed; `.env` is ignored and untracked.
- Repository secret-pattern scan for OpenAI keys, Telegram tokens, and populated credential assignments: passed with no match.

Security coverage verifies numeric Founder authorization and outsider isolation, bootstrap shutdown after Founder configuration, sanitized provider/delivery errors, a secret-free Telegram `/health` response, a secret-free HTTP health response, required webhook secret configuration, and system instructions that explicitly resist message-level instruction override. `.env` remains ignored.

## Known limitations

- Conversation memory is process-local and disappears on restart/redeploy; it is not persistent.
- `/delete_my_data` deletes only AIRA OS process-local conversation state, not data held by Telegram or OpenAI.
- One polling process is mandatory; horizontal scaling is intentionally disabled.
- The Stage A bootstrap should be completed immediately because the bot is not yet locked to the Founder while the numeric ID is empty.
- No live Telegram or OpenAI call is performed by the automated suite.

## Remaining manual Founder actions

1. Have a human merge the deployment PR into `main`; do not auto-merge it.
2. Connect `tsapkovaby-cyber/AIRA-OS` to Render and apply `render.yaml`.
3. Privately set the Telegram token, OpenAI key, model, privacy URL choice, and `TELEGRAM_DELIVERY_MODE=polling`.
4. Complete the two-stage numeric Founder ID bootstrap and redeploy.
5. Confirm one instance, a healthy `/health`, and no other polling/webhook process for the bot.
6. Run the documented Russian memory and command acceptance tests in `@AIRA_influenser_bot`.
