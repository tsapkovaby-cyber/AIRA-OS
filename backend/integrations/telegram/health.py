"""Minimal, secret-free HTTP health endpoint for polling deployments."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from threading import Thread

from .config import TelegramConfig

LOGGER = logging.getLogger(__name__)


def start_health_server(config: TelegramConfig, port: int) -> ThreadingHTTPServer:
    """Serve Render health checks in a daemon thread beside long polling."""
    payload = json.dumps(config.health()).encode("utf-8")

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
            if self.path != "/health":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            LOGGER.info("health request status=%s", args[1] if len(args) > 1 else "unknown")

    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    Thread(target=server.serve_forever, name="health-server", daemon=True).start()
    LOGGER.info("health server started port=%d delivery_mode=%s", port, config.delivery_mode)
    return server
