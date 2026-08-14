"""Short, expiring, tamper-evident inline callback references."""

import base64
import binascii
import hashlib
import hmac
import time

from ..schemas.models import CallbackAction


class InvalidCallback(Exception):
    pass


class CallbackSigner:
    def __init__(self, secret: bytes, *, ttl_seconds: int = 900) -> None:
        if len(secret) < 32:
            raise ValueError("callback secret must contain at least 32 bytes")
        self._secret = secret
        self._ttl = ttl_seconds

    def sign(self, action: CallbackAction, *, now: int | None = None) -> str:
        fields = (action.action, action.object_type, action.object_id)
        if any("|" in field for field in fields):
            raise ValueError("callback fields cannot contain '|'")
        raw = "|".join(
            (*fields, "" if action.version is None else str(action.version), str(int(action.sensitive)),
             str((now or int(time.time())) + self._ttl))
        ).encode()
        body = base64.urlsafe_b64encode(raw).rstrip(b"=")
        signature = hmac.new(self._secret, body, hashlib.sha256).digest()[:8]
        result = (body + b"." + base64.urlsafe_b64encode(signature).rstrip(b"=")).decode()
        if len(result.encode()) > 64:
            raise ValueError("callback reference exceeds Telegram's 64-byte limit")
        return result

    def verify(self, value: str, *, now: int | None = None) -> CallbackAction:
        try:
            body, encoded_signature = value.encode().split(b".", 1)
            if len(encoded_signature) != 11:
                raise InvalidCallback("invalid callback signature")
            padded_signature = encoded_signature + b"=" * (-len(encoded_signature) % 4)
            signature = base64.b64decode(padded_signature, altchars=b"-_", validate=True)
            expected = hmac.new(self._secret, body, hashlib.sha256).digest()[:8]
            if len(signature) != len(expected) or not hmac.compare_digest(signature, expected):
                raise InvalidCallback("invalid callback signature")
            raw = base64.urlsafe_b64decode(body + b"=" * (-len(body) % 4))
            action, object_type, object_id, version, sensitive, expires = raw.decode().split("|")
            if int(expires) < (now or int(time.time())):
                raise InvalidCallback("callback expired")
            return CallbackAction(
                action=action,
                object_type=object_type,
                object_id=object_id,
                version=int(version) if version else None,
                sensitive=bool(int(sensitive)),
            )
        except InvalidCallback:
            raise
        except (binascii.Error, TypeError, UnicodeDecodeError, ValueError) as error:
            raise InvalidCallback("malformed callback") from error
