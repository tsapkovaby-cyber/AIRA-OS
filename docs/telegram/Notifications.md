# Notifications

Delivery levels are `IMPORTANT`, `ACTION_REQUIRED`, `CRITICAL`, and `OPTIONAL`.
Send only Founder-action requests, critical incidents, high-value research,
important task completion and scheduled briefings. Routine internal events and
fine-grained workflow progress are suppressed.

Core and the Scheduler decide whether and when a notification exists. Telegram
only delivers it. Future quiet modes (`NORMAL`, `IMPORTANT_ONLY`, `SILENT`, and
`CRITICAL_ONLY`) remain backend preferences; emergency override policy is also
evaluated there. Delivery failures emit `TelegramDeliveryFailed` for retry by a
backend workflow rather than becoming Telegram-only state.
