# Architecture

```text
Telegram webhook/poller -> TelegramFounderAdapter -> TelegramBotService
  -> immutable ID authentication -> replay/rate guards -> callback verification
  -> AiraCoreGateway -> Decision / Planner / Workflow / Guardian / Publishing
  -> GatewayResponse -> TelegramFounderAdapter -> Telegram API
```

`TelegramFounderAdapter` knows Telegram's update and inline-keyboard shapes. The
application service knows gateway security policy. Neither implements intent
detection or performs agent, approval, workflow, or publication operations.

If Core times out or disconnects, the service returns the explicit unavailable
message and performs no fallback action. Webhook and polling ingress terminate at
the same `receive` boundary, keeping behavior identical.

## Durable boundaries

Normalized inbound messages carry Telegram and internal IDs, conversation ID,
direction, private memory policy and optional workflow reference. Core is
responsible for persisting them. Telegram chat history is context, not persistent
AIRA memory. Core applies the memory candidate and visibility policies.
