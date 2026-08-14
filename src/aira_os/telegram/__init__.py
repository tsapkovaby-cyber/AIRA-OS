"""Telegram transport adapter for AIRA OS (not an intelligence layer)."""

from .app import TelegramApplication
from .config import TelegramConfig

__all__ = ["TelegramApplication", "TelegramConfig"]
