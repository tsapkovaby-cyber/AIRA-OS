"""Tests for environment-backed configuration helpers."""

from __future__ import annotations

import pytest

from backend.core.config.env import read_required_env


def test_read_required_env_loads_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AIRA_TEST_SETTING", "configured")

    assert read_required_env("AIRA_TEST_SETTING") == "configured"


def test_read_required_env_rejects_missing_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AIRA_TEST_SETTING", raising=False)

    with pytest.raises(ValueError, match="AIRA_TEST_SETTING"):
        read_required_env("AIRA_TEST_SETTING")
