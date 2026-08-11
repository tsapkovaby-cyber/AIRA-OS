"""Small local Pydantic-compatible subset for offline Sprint 002 validation.

The project declares the real Pydantic dependency in pyproject.toml. This subset
keeps architecture tests runnable in restricted environments where package
installation is unavailable.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, get_args, get_origin


class ValidationError(ValueError):
    """Validation error compatible with the tests used in this repository."""


class _FieldInfo:
    def __init__(self, default: Any = ..., *, min_length: int | None = None) -> None:
        self.default = default
        self.min_length = min_length


def Field(default: Any = ..., *, min_length: int | None = None) -> Any:
    return _FieldInfo(default, min_length=min_length)


class ConfigDict(dict):
    """Dictionary placeholder matching Pydantic's ConfigDict constructor."""


class BaseModel:
    """Minimal BaseModel supporting typed construction and frozen configs."""

    model_config: ConfigDict = ConfigDict()

    def __init__(self, **data: Any) -> None:
        fields = self._fields()
        for name, info in fields.items():
            if name in data:
                value = data.pop(name)
            elif isinstance(info["default"], _FieldInfo) and info["default"].default is ...:
                raise ValidationError(f"Missing field: {name}")
            elif isinstance(info["default"], _FieldInfo):
                value = info["default"].default
            elif info["default"] is ...:
                raise ValidationError(f"Missing field: {name}")
            else:
                value = info["default"]
            self._validate(name, value, info)
            object.__setattr__(self, name, value)
        if data and self.model_config.get("extra") == "forbid":
            raise ValidationError(f"Unexpected fields: {', '.join(data)}")

    @classmethod
    def _fields(cls) -> dict[str, dict[str, Any]]:
        annotations: dict[str, Any] = {}
        for base in reversed(cls.mro()):
            annotations.update(getattr(base, "__annotations__", {}))
        annotations.pop("model_config", None)
        fields: dict[str, dict[str, Any]] = {}
        for name, annotation in annotations.items():
            default = getattr(cls, name, ...)
            fields[name] = {"annotation": annotation, "default": default}
        return fields

    @staticmethod
    def _validate(name: str, value: Any, info: dict[str, Any]) -> None:
        default = info["default"]
        min_length = default.min_length if isinstance(default, _FieldInfo) else None
        if min_length is not None and isinstance(value, str) and len(value) < min_length:
            raise ValidationError(f"{name} must have at least {min_length} characters")
        annotation = info["annotation"]
        if isinstance(annotation, str):
            return
        origin = get_origin(annotation)
        if origin is not None:
            annotation = origin
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            if not isinstance(value, annotation):
                annotation(value)
        elif annotation in {str, bool} and not isinstance(value, annotation):
            raise ValidationError(f"{name} must be {annotation.__name__}")

    def __setattr__(self, name: str, value: Any) -> None:
        if self.model_config.get("frozen"):
            raise TypeError("Model is frozen")
        object.__setattr__(self, name, value)
