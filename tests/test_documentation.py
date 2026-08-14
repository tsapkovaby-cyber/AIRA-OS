"""Documentation existence checks for Sprint 002."""

from __future__ import annotations

from pathlib import Path

MODULES = ["identity", "decision", "memory", "knowledge", "research", "content", "guardian", "growth"]
DOCS = ["README.md", "Architecture.md", "Interfaces.md", "Future.md", "Examples.md"]


def test_each_module_has_required_documentation() -> None:
    for module in MODULES:
        for doc in DOCS:
            path = Path("backend/core") / module / doc
            assert path.exists(), f"Missing {path}"
            assert path.read_text().strip(), f"Empty {path}"
