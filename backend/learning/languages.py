"""Supported learning and explanation languages for AIRA Academy."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class LanguageSpec:
    code: str
    name: str
    native_name: str
    level_system: str = "CEFR"
    learnable: bool = True
    explanation_supported: bool = True

SUPPORTED_LANGUAGES: tuple[LanguageSpec, ...] = (
    LanguageSpec("en", "English", "English"),
    LanguageSpec("ru", "Russian", "Русский"),
    LanguageSpec("es", "Spanish", "Español"),
    LanguageSpec("it", "Italian", "Italiano"),
    LanguageSpec("tr", "Turkish", "Türkçe"),
    LanguageSpec("kk", "Kazakh", "Қазақ тілі", level_system="AIRA-KZ"),
    LanguageSpec("fr", "French", "Français"),
    LanguageSpec("de", "German", "Deutsch"),
)

_BY_CODE = {language.code: language for language in SUPPORTED_LANGUAGES}
_BY_NAME = {language.name.casefold(): language for language in SUPPORTED_LANGUAGES}


def get_language(value: str) -> LanguageSpec:
    key = value.strip().casefold()
    language = _BY_CODE.get(key) or _BY_NAME.get(key)
    if language is None:
        raise ValueError(f"unsupported language: {value}")
    return language


def learning_languages() -> list[LanguageSpec]:
    return [language for language in SUPPORTED_LANGUAGES if language.learnable]


def explanation_languages() -> list[LanguageSpec]:
    return [language for language in SUPPORTED_LANGUAGES if language.explanation_supported]


def resolve_explanation_language(native_language: str | None, explanation_language: str | None) -> str | None:
    """Prefer an explicit explanation language, otherwise use the learner's native language."""
    candidate = explanation_language or native_language
    if not candidate:
        return None
    return get_language(candidate).name
