# AIRA Telegram MVP v0.1

This integration connects the private Founder Telegram conversation to AIRA through the OpenAI Responses API. Python 3.11+ is recommended.

## Install (macOS or Linux/cloud)

```bash
git clone <repository-url>
cd AIRA-OS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configure

Copy the secret-free template and edit the local file (which Git ignores):

```bash
cp .env.example .env
```

Set `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, and the numeric `AIRA_FOUNDER_TELEGRAM_ID`. Export the file without printing it:

```bash
set -a; source .env; set +a
```

The model is configurable with `AIRA_MODEL` (default: `gpt-4.1-mini`). Optionally set `PRIVACY_POLICY_URL`.

To safely discover the numeric Founder ID during initial setup, leave `AIRA_FOUNDER_TELEGRAM_ID` unset, start the bot, and privately send `/start`; the bot returns the sender's numeric ID. Stop it, configure that number, and restart. This setup response is automatically disabled once configured. Never use a username for authentication.

## Start and stop

Development long polling (default):

```bash
python -m backend.integrations.telegram.bot
```

Stop with **Ctrl-C**. In a cloud process manager, send `SIGTERM` or use the provider's stop/restart control.

Production webhook mode (do not run a polling instance at the same time):

```bash
export TELEGRAM_DELIVERY_MODE=webhook
export TELEGRAM_WEBHOOK_URL=https://your-host.example/telegram
export TELEGRAM_WEBHOOK_SECRET=<set-in-your-secret-manager>
export PORT=8080
python -m backend.integrations.telegram.bot
```

Only one delivery mode is selected per process. The public URL must be HTTPS and route to the configured port. The webhook secret is validated through Telegram's secret-token header; it is never placed in a URL.

## Test

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

Manual acceptance test in `@AIRA_influenser_bot`:

1. Send `Аира, привет` and confirm a natural Russian response.
2. Send `Ты помнишь, что я только что написала?` and confirm the answer uses recent context.
3. Check `/start`, `/help`, `/privacy`, `/health`, and `/delete_my_data`.

Conversation state is process-local and is lost on restart. `/delete_my_data` deletes the requester's local state only; it does not claim deletion by Telegram or OpenAI.
