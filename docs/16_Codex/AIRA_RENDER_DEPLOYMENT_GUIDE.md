# AIRA Telegram MVP — Render deployment guide

This guide deploys the existing private MVP in **long-polling mode**. Keep exactly one Render instance: two polling processes cannot safely use the same Telegram bot. Do not paste secrets into GitHub, documentation, logs, or chat.

## STEP 1 — Open Render

1. Open <https://dashboard.render.com/> and sign in.
2. Choose **New +** → **Blueprint**.

Success: Render shows the Blueprint connection screen.

## STEP 2 — Connect GitHub

1. Select **Connect GitHub**.
2. Authorize Render to see the required repository (repository-only access is sufficient).

Success: the repository appears in Render's list.

## STEP 3 — Select tsapkovaby-cyber/AIRA-OS

Select **tsapkovaby-cyber/AIRA-OS** and the `main` branch after this deployment PR has been merged by a human.

Success: Render finds `render.yaml` at the repository root.

## STEP 4 — Deploy Blueprint / render.yaml

1. Click **Apply** or **Deploy Blueprint**.
2. Confirm the service name `aira-telegram-mvp`, runtime **Python**, start command `python -m backend.integrations.telegram.bot`, and one instance.
3. Do not increase the instance count. Automatic deploy/restart and `/health` checks are configured by the Blueprint.

Success: the build installs `requirements.txt`; the first start waits for the environment values below.

## STEP 5 — Add environment variables

Open **aira-telegram-mvp → Environment**. Add/save these exact fields (never include surrounding quotes):

| Exact field name | Value | Secret? | Success looks like |
|---|---|---:|---|
| `TELEGRAM_BOT_TOKEN` | Token obtained privately from Telegram BotFather | Yes | Render shows the value as hidden |
| `OPENAI_API_KEY` | Active project API key from the OpenAI dashboard | Yes | Render shows the value as hidden |
| `AIRA_FOUNDER_TELEGRAM_ID` | Leave empty for Stage A only; later enter the numeric ID returned by `/start` | Private identifier | Empty during bootstrap, digits only after Step 7 |
| `AIRA_MODEL` | OpenAI model available to the project, for example `gpt-4.1-mini` | No | A non-empty model name is saved |
| `PRIVACY_POLICY_URL` | Public HTTPS policy URL, or leave empty to use the private-testing notice | No | `/privacy` shows the URL or temporary notice |
| `TELEGRAM_DELIVERY_MODE` | Exactly `polling` | No | Logs say polling; no webhook is enabled |

Future webhook-only fields—leave empty during this deployment:

| Exact field name | Value when webhook mode is deliberately enabled later | Secret? | Success looks like |
|---|---|---:|---|
| `TELEGRAM_WEBHOOK_URL` | Public HTTPS URL ending in `/telegram` | No | Telegram updates reach the service without a token in the URL |
| `TELEGRAM_WEBHOOK_SECRET` | New high-entropy random secret | Yes | Requests without the matching secret header are rejected |
| `PORT` | Render-provided port; normally do not set it manually | No | Render routes to the bound service port |

Success: all required values are saved, with credentials hidden. Do not display or copy them into logs.

## STEP 6 — Stage A Founder ID bootstrap

1. Keep `AIRA_FOUNDER_TELEGRAM_ID` empty.
2. Deploy once and wait for **Live**.
3. In a private chat with `@AIRA_influenser_bot`, send `/start`.
4. Copy only the numeric Telegram user ID the bot returns. Do not use a username.

Success: `/start` returns the sender's numeric ID. Do not hold conversations before locking the bot to the Founder.

## STEP 7 — Add AIRA_FOUNDER_TELEGRAM_ID

Return to **Environment**, edit `AIRA_FOUNDER_TELEGRAM_ID`, paste the digits from Step 6, and save.

Success: the field contains digits only. Treat it as a private identifier, not as an authentication username.

## STEP 8 — Redeploy

Choose **Manual Deploy → Deploy latest commit** (or allow the environment save to redeploy). Wait until the service is **Live** and `/health` is healthy.

Success: `/start` shows the normal AIRA greeting and **does not reveal a Telegram ID**. An unrelated Telegram account receives only the access-denied response.

## STEP 9 — Telegram acceptance test

In `@AIRA_influenser_bot`, test in order:

1. `Аира, привет` → a natural Russian response.
2. `Запомни кодовое слово: фиолетовый.`
3. `Какое кодовое слово я назвала?` → the answer includes `фиолетовый`.
4. `/start`, `/help`, `/privacy`, `/health`, and `/delete_my_data` → each returns a safe response.
5. After `/delete_my_data`, confirm the bot does not claim deletion from Telegram or OpenAI.

Memory is process-local and is lost at every restart or redeploy. It is not permanent storage.

## STEP 10 — Troubleshooting

- **Build fails:** verify the Blueprint build command is `python -m pip install -r requirements.txt` and Python is 3.11 or newer.
- **Missing configuration:** check exact variable names; never paste their values into a support ticket or logs.
- **Bot does not reply:** ensure the service is Live, `TELEGRAM_DELIVERY_MODE=polling`, and no local/second cloud polling process uses the same bot.
- **Conflict error from Telegram:** scale back to exactly one instance and stop every other polling deployment. Polling startup selects Telegram `getUpdates` and clears the bot's registered webhook; nevertheless, stop every webhook deployment before polling so only one delivery process remains.
- **Founder denied:** `AIRA_FOUNDER_TELEGRAM_ID` must be the numeric ID returned in Stage A, not `@username`; save and redeploy.
- **ID still appears:** the Founder variable is still empty or was not deployed. Configure it immediately and redeploy.
- **AI errors:** verify the OpenAI key, model availability, and project billing privately.
- **Health check:** open the Render service's `/health`; it should report status/configuration booleans and delivery mode only—never credentials, Founder ID, prompts, or messages.

Webhook is deliberately not enabled for this initial deployment. A future switch must set all three webhook fields, keep the URL free of secrets, stop polling first, and retain a single delivery mode.
