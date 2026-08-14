# Approval flow

1. Core renders the current item version, Guardian result, workflow state and risk.
2. The gateway signs a short-lived object/action/version reference for the button.
3. On callback, the gateway authenticates the immutable Telegram ID, verifies the
   signature and expiry, checks the action permission and claims the update ID.
4. Core re-loads the object and applies the same freshness, version, Guardian and
   workflow checks used by the Dashboard.
5. Sensitive actions first produce a new confirmation challenge. Only a second,
   valid callback may cause Core to transition the workflow.
6. Publishing remains a Publishing Engine operation; the Telegram handler never
   calls a channel API.

Changed, expired, malformed, replayed or unauthorized approvals fail closed.
Callback data is only a signed reference: Core must always validate server-side
state and record the audit event.
