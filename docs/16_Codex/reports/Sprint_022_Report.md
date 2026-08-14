# Sprint 022 Report — AIRA Telegram Presence & Interaction Platform

## Summary

Sprint 022 delivers a cloud-ready Telegram transport module around AIRA OS. Telegram performs authentication, normalization, durable ingestion, media transport, concise response delivery, and exact proposal callbacks; canonical intelligence remains behind platform-neutral Core, Memory, Perception, Research, Guardian/Approval, and Speech ports.

## Telegram Architecture

`POST /integrations/telegram/webhook` verifies Telegram's secret header and idempotently inserts the update into a durable SQLite queue before returning `202`. A separate worker normalizes and authorizes the update, resolves its session/media/reply context, invokes AIRA services, and sends the result through the Bot API. Webhook and long polling are mutually exclusive configuration modes.

## Bot Configuration

Configuration is environment-only: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `AIRA_FOUNDER_TELEGRAM_ID`, optional identity/environment fields, storage paths, media limit, private mode, and delivery mode. `.env.example` contains blank placeholders. The username is not hardcoded. Configuration diagnostics redact both secrets.

## Founder Authentication

Private Founder mode is the default. User IDs are checked before session creation or Core/Memory access. Founder commands and proposal callbacks require the configured identity; callback decisions also require proposal ownership.

## Conversation Engine

`ConversationSession` persists platform/chat/user identity, canonical AIRA identity version, mode, memory context, timestamps, and status. The Store retains a bounded recent transcript and exposes a Memory adapter boundary. Reply metadata is normalized. Natural messages go to AIRA Core; Telegram defines no separate personality.

## Multimodal Messaging

Voice, audio, photo, video, and document metadata are normalized. Downloads enforce a configured byte limit and use opaque Telegram IDs for local names. Photo/video/document inputs pass to the Sprint 021-compatible Perception port with captions. Content is treated as input, never policy or Constitution instructions. Video review architecture is present through the same port.

## Voice Messaging

Voice/audio files are downloaded and passed to the Speech transcription port before Core reasoning. `/voice` describes supported reply preferences; safe MVP default remains text.

## AIRA Voice Responses

The Speech port includes synthesis with the canonical voice, and Gateway exposes voice delivery. Deployments can enable this without placing voice identity in Telegram-specific intelligence. Automated MVP responses remain text by default.

## Memory Integration

The worker requests recent Memory context, sends conversation turns through the Memory policy's `consider` boundary, and otherwise uses bounded durable session history. Unauthorized users reach neither mechanism.

## Research Integration

`/research <topic>` delegates to the Core research orchestrator and immediately returns its acknowledgement. The autonomy kill switch blocks starting research. External risk and cost decisions remain subject to Core/Guardian approval policy.

## Approval UX

`ActionProposal` includes ID, action, reason, risk, cost, preview, requester, timestamps, status, and expiry. Inline callback data is `proposal:<exact-id>:approve|reject`. Atomic pending-state updates ensure approval occurs once; labels alone cannot approve anything. Telegram does not execute publishing itself.

## Security

Controls cover constant-time webhook verification, Founder isolation, proposal ownership, duplicate update IDs, rate limiting, payload/media limits, bounded history, structured metadata-only audit events, secret redaction, generic errors, and `/pause`/`/resume` autonomy control. Bot tokens are not logged, stored in Memory, or committed.

## Deployment

The deployment guide documents official bot setup, cloud secret storage, TLS webhook registration, always-on service/worker topology, persistent storage, monitoring, staging smoke tests, and rotation. Separate bots/tokens are recommended per environment.

## Tests

Automated tests cover normalization, webhook authentication, authorization and memory isolation, commands, callback ownership and idempotency, update idempotency, sessions, bounded history, multimodal handling, kill switch/research, redaction, and WSGI error handling. They exercise Gateway → durable queue → Worker → Core → response with fake Telegram transport.

## End-to-End Results

- **Text chat:** passed locally end-to-end through webhook ingestion, queue, session, Core, history, and response transport.
- **Voice/photo/document:** passed with downloaded fake media and Speech/Perception adapters.
- **Research, status, tasks, kill switch:** passed through command routing.
- **Approval and callback forgery:** passed; exact proposal changed once, unauthorized callback denied.
- **Error recovery:** worker records sanitized error type and sends a safe user message.
- **Live Telegram:** pending Founder-owned token, bot account, public HTTPS endpoint, and connected production AIRA service providers. No credential was available or requested in the repository environment.

## Known Limitations

- Live Bot API connectivity and canonical media engines cannot be proven without deployment credentials and Sprint 001–021 runtime adapters.
- SQLite is suitable for an initial single-worker deployment; horizontally scaled production should supply a transactional shared Store/queue.
- Voice preference persistence, proactive notification delivery, quiet hours, digest mode, individual module kill switches, and Mini App UI are extension-ready but not active MVP behavior.
- `send_voice` is the transport seam; production multipart upload or Telegram file-ID reuse should be selected by the deployed transport.

## Recommendations for Sprint 023

After Founder approval of this sprint, validate staging with a Founder-owned bot and real service adapters; add a shared production queue/store before horizontal scaling; then implement persisted voice/notification preferences and operational dashboards. Sprint 023 was not started.
