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
    writing_system: str | None = None
    aliases: tuple[str, ...] = ()

SUPPORTED_LANGUAGES: tuple[LanguageSpec, ...] = (
    LanguageSpec("en", "English", "English", writing_system="Latin"),
    LanguageSpec("ru", "Russian", "Русский", writing_system="Cyrillic"),
    LanguageSpec("es", "Spanish", "Español", writing_system="Latin"),
    LanguageSpec("it", "Italian", "Italiano", writing_system="Latin"),
    LanguageSpec("tr", "Turkish", "Türkçe", writing_system="Latin"),
    LanguageSpec("kk", "Kazakh", "Қазақ тілі", level_system="AIRA-KZ", writing_system="Cyrillic"),
    LanguageSpec("fr", "French", "Français", writing_system="Latin"),
    LanguageSpec("de", "German", "Deutsch", writing_system="Latin"),
    LanguageSpec("ko", "Korean", "한국어", level_system="AIRA-KR", writing_system="Hangul"),
    LanguageSpec("zh", "Mandarin Chinese", "简体中文", level_system="HSK", writing_system="Simplified Chinese", aliases=("Chinese", "Mandarin", "Simplified Chinese")),
)

_BY_CODE = {language.code: language for language in SUPPORTED_LANGUAGES}
_BY_NAME = {language.name.casefold(): language for language in SUPPORTED_LANGUAGES}
_BY_ALIAS = {alias.casefold(): language for language in SUPPORTED_LANGUAGES for alias in language.aliases}


def get_language(value: str) -> LanguageSpec:
    key = value.strip().casefold()
    language = _BY_CODE.get(key) or _BY_NAME.get(key) or _BY_ALIAS.get(key)
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
