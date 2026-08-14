from __future__ import annotations

import json
from .audit import Audit
from .gateway import TelegramGateway
from .security import Security
from .storage import Store
from .worker import TelegramWorker


class TelegramApplication:
    """Composition root and fast webhook ingestion boundary."""
    def __init__(self, config, core, perception=None, speech=None, memory=None, gateway=None, store=None):
        self.config = config
        self.store = store or Store(config.database_path)
        self.gateway = gateway or TelegramGateway(config)
        self.security = Security(config.founder_id, config.webhook_secret, config.private_founder_mode)
        self.audit = Audit()
        self.worker = TelegramWorker(self.store, self.gateway, self.security, core, perception, speech, memory, self.audit)

    def ingest(self, secret: str, update: dict) -> tuple[int, dict]:
        if not self.security.verify_webhook(secret):
            self.audit.emit("TelegramAuthFailed", reason="invalid_webhook_secret")
            return 401, {"ok": False}
        try: update_id = int(update["update_id"])
        except (KeyError, TypeError, ValueError): return 400, {"ok": False}
        accepted = self.store.enqueue_once(update_id, update)
        return 202, {"ok": True, "queued": accepted}

    def wsgi(self, environ, start_response):
        if environ.get("PATH_INFO") != "/integrations/telegram/webhook" or environ.get("REQUEST_METHOD") != "POST":
            start_response("404 Not Found", [("Content-Type", "application/json")]); return [b'{"ok":false}']
        length = int(environ.get("CONTENT_LENGTH") or 0)
        if length > 1024 * 1024:
            start_response("413 Payload Too Large", []); return [b""]
        try: payload = json.loads(environ["wsgi.input"].read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            start_response("400 Bad Request", [("Content-Type", "application/json")]); return [b'{"ok":false}']
        status, response = self.ingest(environ.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN", ""), payload)
        labels = {202:"202 Accepted",400:"400 Bad Request",401:"401 Unauthorized"}
        start_response(labels[status], [("Content-Type", "application/json")]); return [json.dumps(response).encode()]

    def health(self) -> dict:
        return {"telegram": "configured", "queue": "healthy", "aira_backend": "configured", "delivery_mode": self.config.delivery_mode}
