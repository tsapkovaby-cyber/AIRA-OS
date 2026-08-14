# Sprint 032 — Placement & Level Assessment

AIRA Academy now has a transport-independent placement layer in `backend/learning/placement.py`.

The MVP uses deterministic scoring so tests and onboarding do not require paid AI calls. A placement assessment contains typed questions with skill and level metadata, accepts student answers, derives an overall level and per-skill scores, stores the result for the authenticated Student, updates `LearningProfile.current_level`, and can recommend an existing course matching the target language and resulting level.

The reference assessment currently uses CEFR labels A1–C2. The assessment object also stores `level_system`, so Sprint 033 can support language-specific schemes without hard-wiring every language to CEFR.

Placement target language is independent from the future explanation/interface language. Sprint 033 will introduce the multilingual catalog and explicit explanation-language selection for English, Spanish, Italian, Turkish, Kazakh, French and German.

The current scoring engine is intentionally replaceable. Future adaptive assessment may add listening, speaking, free-text scoring and AI-assisted evaluation behind the same domain boundary while preserving deterministic fallback behavior.
