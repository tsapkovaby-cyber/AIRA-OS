"""Environment-variable configuration helpers."""

from __future__ import annotations

import os


def read_required_env(name: str) -> str:
    """Read a required environment variable."""

    value = os.getenv(name)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value
