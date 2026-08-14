import json
import logging


class Audit:
    def __init__(self, logger=None): self.logger = logger or logging.getLogger("aira.telegram.audit")
    def emit(self, event: str, **fields):
        # Message bodies and credentials are deliberately excluded by callers.
        self.logger.info(json.dumps({"event": event, **fields}, sort_keys=True))
