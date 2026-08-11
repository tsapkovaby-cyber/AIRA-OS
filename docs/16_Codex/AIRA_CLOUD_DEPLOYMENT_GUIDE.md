# AIRA Cloud Deployment Guide (Render)

This guide deploys the existing **@AIRA_influenser_bot**. Do not create another bot and never paste a secret into Codex, a Git file, or a support message.

## Required environment variables

| Variable | Source | Secret |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather | **YES** |
| `OPENAI_API_KEY` | OpenAI API Platform | **YES** |
| `AIRA_FOUNDER_TELEGRAM_ID` | Telegram bootstrap `/start` | **treat as private identifier** |
| `AIRA_MODEL` | deployment configuration | **NO** |
| `PRIVACY_POLICY_URL` | AIRA Privacy Policy | **NO** |

Render encrypts secret environment values. The initial mode is polling, exactly one instance, while the web service also supplies an HTTPS health endpoint. Your Mac may be switched off.

## STEP 1 — Make the two secret values available

1. Open Telegram and open the verified **@BotFather** chat. Use its token-management command for the existing **@AIRA_influenser_bot**. The value belongs in the field named `TELEGRAM_BOT_TOKEN`; it is **secret**. Do not create a bot.
2. Open **https://platform.openai.com/api-keys**, sign in to the AIRA API account, and press **Create new secret key** only if the account does not already have a deployable key. The value belongs in `OPENAI_API_KEY`; it is **secret** and is shown once.
3. Success looks like having both values ready to enter directly into Render, without putting either in this repository or chat.

## STEP 2 — Create the Render service (STAGE A)

1. Open **https://dashboard.render.com/** and sign in. Press **New +**, then **Blueprint**.
2. Connect the GitHub repository containing AIRA OS. In **Blueprint Name**, keep the suggested name; select the branch containing this preparation and press **Apply**. Render reads `render.yaml`.
3. On the environment-value screen fill these fields:
   * `TELEGRAM_BOT_TOKEN`: paste the BotFather value directly; **secret YES**.
   * `OPENAI_API_KEY`: paste the OpenAI Platform value directly; **secret YES**.
   * `AIRA_MODEL`: enter the approved OpenAI model name used by AIRA; **secret NO**.
   * `PRIVACY_POLICY_URL`: enter the public HTTPS AIRA privacy-policy URL, or leave empty for the temporary private-test notice; **secret NO**.
   * `AIRA_FOUNDER_TELEGRAM_ID`: **leave empty in STAGE A**; treat it as a private identifier.
   * Leave `TELEGRAM_DELIVERY_MODE` as `polling`. Do not set webhook variables yet.
4. Press **Apply** / **Deploy**. Open the service, then the **Logs** tab. Success looks like a green **Live** status and `service_started mode=polling`. The start command is exactly `python -m backend.integrations.telegram.bot`.
5. In the service **Settings** page confirm **Health Check Path** is `/health` and **Instance Count** is `1`. Never raise it while polling.

## STEP 3 — Capture the numeric Founder ID (STAGE A)

1. Open Telegram, open **@AIRA_influenser_bot** in a private chat, and send `/start`.
2. AIRA returns the sender's numeric Telegram ID. Record it privately. This is the value for `AIRA_FOUNDER_TELEGRAM_ID`; treat it as a private identifier.
3. Success looks like a digits-only response. If it does not arrive, inspect Render **Logs** for a configuration error category—never post tokens in support chat.

## STEP 4 — Lock the service to the Founder (STAGE B)

1. Return to Render → **aira-telegram-mvp** → **Environment**. Find `AIRA_FOUNDER_TELEGRAM_ID`, press **Edit**, enter the digits recorded in STEP 3, and press **Save Changes**. This value is a private identifier.
2. Select **Save and deploy** (or **Manual Deploy → Deploy latest commit**) so the process restarts.
3. Open **@AIRA_influenser_bot** and send `/start` again. Success looks like `Аира на связи.` The numeric bootstrap ID must no longer appear. A different Telegram numeric user ID remains unauthorized; username similarity never grants access.

## STEP 5 — Run the Founder acceptance test

In the same private Telegram chat send, one at a time:

1. `Аира, привет` — success is a natural Russian answer.
2. `Запомни кодовое слово для этого теста: фиолетовый.`
3. `Какое кодовое слово я только что назвала?` — success includes `фиолетовый`.
4. Send `/privacy`, then `/delete_my_data`. Success is a policy URL (or temporary notice) and an accurate confirmation that only local AIRA history was deleted.

The current conversation memory is process-local and is lost on restart/redeploy. This is a known MVP limitation, not durable storage.

## STEP 6 — Webhook mode later, not now

Wait until the Render public URL is known. For a later controlled switch, set `TELEGRAM_DELIVERY_MODE=webhook`, set `TELEGRAM_WEBHOOK_URL` to the service's **HTTPS origin** (no secret query parameter), generate a strong secret directly in a password manager for `TELEGRAM_WEBHOOK_SECRET`, and keep `PORT` supplied by Render. Redeploy only after all three are present. The app registers `/telegram`, validates Telegram's secret header, and continues serving `/health`.
