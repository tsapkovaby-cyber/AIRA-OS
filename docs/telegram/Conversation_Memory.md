# Conversation memory

Telegram history is not AIRA memory. Core processes a message through conversation
context, relevant summary, important-fact extraction, memory candidacy and memory
policy before durable storage. The gateway labels initial messages
`FOUNDER_PRIVATE`; Content and Research agents receive no implicit access.

Project, decision and knowledge questions are forwarded to Core, which queries the
Memory and Knowledge engines and returns a compact answer. Long material should be
summarized with a secure Dashboard deep link instead of being copied into chat.
