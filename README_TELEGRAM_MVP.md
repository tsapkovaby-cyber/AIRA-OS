# AIRA Telegram MVP

The private MVP runs as one Python process. Its production start command is:

```bash
python -m backend.integrations.telegram.bot
```

Polling is the initial delivery mode and `render.yaml` fixes the service at one instance. Telegram's polling startup removes any previously configured webhook. The same entry point supports a future HTTPS webhook when its public URL is known; it validates Telegram's secret-token header.

Conversation history uses `ConversationMemory` and the current `ProcessLocalConversationMemory`. It is **not persistent**: a restart or redeploy erases it. The protocol is the replacement boundary for a later durable store.

`GET /health` returns only service state, whether Telegram and AI configuration are present, and delivery mode. Application logs contain event names, latency, and exception class—not message bodies, memory, prompts, tokens, keys, or environment dumps.

See [`docs/16_Codex/AIRA_CLOUD_DEPLOYMENT_GUIDE.md`](docs/16_Codex/AIRA_CLOUD_DEPLOYMENT_GUIDE.md) for deployment.
