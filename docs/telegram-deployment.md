# Telegram deployment

## Bot setup

1. The Founder creates separate development/staging/production bots with Telegram's official bot-management flow, sets the display name to **AIRA**, description to **Virtual AI creator and assistant**, and uploads the approved canonical image.
2. Put `TELEGRAM_BOT_TOKEN`, a random `TELEGRAM_WEBHOOK_SECRET`, and `AIRA_FOUNDER_TELEGRAM_ID` in the cloud secret manager. Never put values in source, logs, Memory, or model context.
3. Configure an always-on Python 3.11+ service, persistent SQLite volume (or a compatible production Store implementation), durable media storage, and one worker process.
4. Expose TLS endpoint `POST /integrations/telegram/webhook`. Register it through Telegram `setWebhook`, passing the public URL and `secret_token` matching `TELEGRAM_WEBHOOK_SECRET`.
5. Run the WSGI application and repeatedly call `app.worker.run_once()` from the worker. Use either webhook or long polling, never both.

## Production checklist

- Keep `PRIVATE_FOUNDER_MODE=true`; validate the Founder ID with a direct message before enabling workflows.
- Restrict ingress, cap request/media sizes, persist the database, encrypt storage, set backups, and configure structured-log retention.
- Connect platform-neutral Core, Memory, Perception, Research, Guardian/Approval, and canonical Speech adapters at `TelegramApplication` composition.
- Monitor queue age, failed updates, bot connectivity, provider health, and last successful update. Alert without message bodies or secrets.
- Rotate the bot token immediately on suspected exposure. Revoke the old token through Telegram and update the secret manager.
- Smoke-test text, voice, image, document, callback ownership/idempotency, `/pause`, and unauthorized-user isolation in staging before production.

Real Telegram delivery requires Founder-owned credentials and a public HTTPS deployment; automated tests use a faithful transport fake and do not require secrets.
