"""Sprint 002 initialization, configuration, and validation tests."""

from __future__ import annotations

import importlib

import pytest
from pydantic import ValidationError

MODULES = [
    ("identity", "Identity"),
    ("decision", "Decision"),
    ("memory", "Memory"),
    ("knowledge", "Knowledge"),
    ("research", "Research"),
    ("content", "Content"),
    ("guardian", "Guardian"),
    ("growth", "Growth"),
]


@pytest.mark.parametrize(("module_name", "class_prefix"), MODULES)
def test_engine_initializes(module_name: str, class_prefix: str) -> None:
    module = importlib.import_module(f"backend.core.{module_name}")
    config_cls = getattr(module, f"{class_prefix}Config")
    engine_cls = getattr(module, f"{class_prefix}Engine")

    config = config_cls(
        engine_name=f"{module_name}-engine",
        required_environment_key=f"AIRA_{module_name.upper()}_ENGINE_NAME",
    )
    result = engine_cls(config).initialize()

    assert result.engine_name == f"{module_name}-engine"
    assert result.initialized is True


@pytest.mark.parametrize(("module_name", "class_prefix"), MODULES)
def test_configuration_is_externalized(module_name: str, class_prefix: str) -> None:
    module = importlib.import_module(f"backend.core.{module_name}")
    config_cls = getattr(module, f"{class_prefix}Config")

    config = config_cls(
        engine_name=f"{module_name}-engine",
        enabled=False,
        required_environment_key=f"AIRA_{module_name.upper()}_ENGINE_NAME",
    )

    assert config.required_environment_key.startswith("AIRA_")
    assert config.enabled is False


@pytest.mark.parametrize(("module_name", "class_prefix"), MODULES)
def test_configuration_validation_rejects_empty_names(module_name: str, class_prefix: str) -> None:
    module = importlib.import_module(f"backend.core.{module_name}")
    config_cls = getattr(module, f"{class_prefix}Config")

    with pytest.raises(ValidationError):
        config_cls(engine_name="", required_environment_key=f"AIRA_{module_name.upper()}_ENGINE_NAME")
