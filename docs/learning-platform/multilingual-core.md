# Multilingual Learning Core — Sprint 033

AIRA Academy supports eight learning languages: English, Russian, Spanish, Italian, Turkish, Kazakh, French, and German.

The learner profile separates the language being learned from the language used to explain material. `target_languages` contains learning targets. `explanation_language` controls explanations from AIRA and is also the canonical application UI language for the learner. If no explicit explanation language is chosen, the supported `native_language` becomes the default.

This means the same course can be used by learners with different interface and explanation languages. For example, a learner may study German with Russian explanations, Russian with English explanations, or English with Turkish explanations.

The language registry is data-driven so future languages can be added without creating a second learning architecture. Each language also exposes a `level_system`. Most initial language paths use CEFR. Kazakh is explicitly marked with an independent `AIRA-KZ` level-system boundary so the curriculum can later adopt the most appropriate proficiency framework without changing account, progress, or course ownership logic.

The web application should localize navigation, forms, instructions, errors, onboarding, placement-test guidance, course descriptions where translated content exists, and AIRA instructional explanations using the resolved application language. The target-language content itself remains in the language being studied.

Sprint 033 creates course shells rather than claiming that complete A1–C2 curricula already exist. Dedicated curriculum/content sprints must author and review lessons for each language before production publication.
