# Sprint 037 — Korean & Mandarin Chinese Expansion

AIRA Academy now supports ten learning and explanation languages by adding Korean and Mandarin Chinese to the shared multilingual catalog.

## Korean
- code: `ko`
- native label: `한국어`
- writing system: Hangul
- level system is represented independently so the platform is not hard-coded to CEFR.

## Mandarin Chinese
- code: `zh`
- native label: `简体中文`
- initial written form: Simplified Chinese
- level system: HSK
- accepted aliases include Chinese, Mandarin, and Simplified Chinese.

The data model keeps the writing system separate from the language identity so Traditional Chinese can be added later without redesigning the learning core.

Both languages are available as target languages and explanation/application languages. Voice Tutor uses the same catalog, so no paid speech integration is required for regression testing.
