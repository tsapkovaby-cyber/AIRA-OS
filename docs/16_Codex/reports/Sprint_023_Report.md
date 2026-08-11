# Sprint 023 Report — AIRA Academy & Language Tutor

## Summary

Sprint 023 establishes **AIRA Academy** as a transport-neutral product domain alongside, not in place of, AIRA Core. Its first product, **AIRA Languages**, supports the Russian-to-English and English-to-Russian conversational learning tracks. The implementation follows the attempt → analysis → hint/correction → explanation → retry → feedback → memory → review loop and deliberately avoids translation-only teaching.

## AIRA Academy Architecture

The `backend.education` package separates domain models, students, assessment, curriculum, lessons, conversation, vocabulary/review, grammar, pronunciation, progress, tandem preparation, guardian policy, and curated language tracks. `EducationAPI` is the application facade for Telegram and future web clients. Provider interfaces isolate speech services. No Academy code changes AIRA's Constitution, canonical personality, or general conversation memory.

## Student Profiles

`StudentProfile` captures platform identity, native and target languages, CEFR-like estimate, goals, interests, lesson preferences, confidence, vocabulary and language profiles, strengths/weaknesses, schedule, skill progress, safety mode, and timestamps. Validation rejects identical native/target languages, unsupported lesson lengths, and invalid confidence values. Founder status has no special route into educational data; a Founder is a student only through a distinct `StudentProfile`.

## Educational Memory and Isolation

`LearningMemory` contains only goals, educational progress, error bank, vocabulary, lesson history, assessments, and learning preferences. The repository requires both student ID and owning platform-user ID on every scoped read. A mismatched or unknown owner fails closed with `StudentAccessDenied`. Tandem preparation accepts IDs and public prompts but never either learner's memory. Telegram deletion removes both recent conversation data and educational records.

## Assessment Engine

Assessment starts as an adaptive conversation rather than a large exam. Stages cover introduction, basic questions, comprehension, response, vocabulary, grammar, and optional voice. Results preserve separate skill measurements, strengths, weaknesses, a starting recommendation, and confidence. Every result explicitly states that it is a learning estimate and not formal CEFR certification.

## Curriculum Engine

The engine selects a curated language track, matches the estimated level, considers learner interests, skips completed topics, and gently raises or lowers difficulty from recent performance. Learning plans define measurable conversational goals, target level, track-specific priorities, topic sequence, adaptive active-recall review, and lightweight monthly reassessment.

## Lesson Engine

Lesson plans cover objectives, contextual vocabulary and grammar, speaking, listening, pronunciation, due review, duration, and difficulty. Profiles support 5, 15, 20, 30, 45, and 60 minutes. Five-minute plans provide a phrase/context, listening item, mini dialogue, and active-recall prompt. Finishing a lesson stores performance and updates learning and speaking minutes before generating a concise post-lesson report.

## Conversation Practice

Conversation sessions support casual-friend, tutor, immersion, and future-ready tandem modes. Target-language use rises with proficiency, while immersion forces target-language-only interaction (clients can map “Explain” to support-language help). Corrections are buffered until feedback. Soft mode returns at most the two highest-value corrections; standard mode prioritizes recurring or communication-affecting errors; intensive mode returns detail. The four-step hint ladder records a progression from context to full answer.

`ScenarioEngine` provides real-life roles such as barista, receptionist, airport employee, colleague, and neighbour while keeping pedagogical behavior in Academy rather than Telegram.

## English Track

The curated skeleton spans Pre-A1 through B2, beginning with introductions and cafe interaction, then travel problems, technology, and nuanced workplace opinions. RU → EN priorities are listening, speaking, and high-frequency vocabulary, with grammar supporting communication. The pilot path begins with a 60/40 target/support-language ratio at A1 and increases target-language exposure with demonstrated level.

## Russian Track

The Russian skeleton spans Pre-A1 through B2 with marked stress in beginner vocabulary. It prioritizes spoken utility, pronunciation, common vocabulary, cases through functions such as “Я живу в Лондоне,” listening, and conversation. It does not begin with six-case tables or excessive terminology.

## Voice Learning

`VoiceLessonService` abstracts recognition and synthesis. Recognition below the confidence threshold requests repetition and explicitly records no learner mistake. Synthesis always receives `AIRA_VOICE_IDENTITY_V1` plus the relevant English- or Russian-teacher speech profile, representing the same AIRA rather than separate personalities. Speed is bounded while preserving identity. Pronunciation analysis is provider-neutral and returns actionable, non-judgmental feedback when technically available.

## Vocabulary System

Vocabulary items retain meaning, context, example, CEFR-like level, review history, recall strength, next review, mistakes, and state. The complete NEW/LEARNING/WEAK/FAMILIAR/MASTERED/REVIEW_REQUIRED lifecycle is represented. Lesson review asks for active retrieval rather than passive rereading.

## Error Bank

Language mistakes retain original and corrected forms, category, explanation, severity, recurrence, timestamps, and mastery status inside one learner's isolated memory. Correction selection prioritizes severity and recurrence without interrupting every conversational error.

## Spaced Review

`ReviewScheduler` computes an adaptive interval from recall strength, repeated errors, item importance, and goal relevance. Weak recall increases error pressure and brings review forward. Due items are ordered by weakness and error count rather than a universal fixed schedule.

## Progress Analytics

The dashboard keeps separate speaking, listening, vocabulary, grammar, reading, writing, and pronunciation skills instead of a misleading universal score. It also records completed lessons, learning and speaking minutes, vocabulary learned/retained, recurring mistakes, estimated level, and streak. The model supports weekly summaries and monthly baseline comparisons without unnecessary profiling.

## Telegram Integration

`/learn` is registered by the existing Telegram application and routed through a thin `TelegramEducationAdapter` into `EducationAPI`. New learners receive the requested onboarding questions; existing learners receive the Academy menu. Telegram contains no teaching rules. The same API can serve the future Academy web experience. Text lessons work today; voice messages can be submitted through the provider-neutral API when a Telegram binary-media adapter and configured speech provider are supplied.

## Education Guardian

The guardian supports adult and minor modes, rejects unsafe minor examples, secrecy manipulation, direct completion of assessed homework, and unverified teaching claims. It expresses the future School principle of teaching, guiding, and checking rather than doing the student's work. Public child access still requires a complete age-policy and consent design.

## Pilot Results

Automated seven-day content sequencing is represented by the reusable assessment, lesson, scenario, conversation, review, and reporting primitives; the repository does not simulate human retention over seven wall-clock days. Automated E2E pilots for RU → EN and EN → RU each completed student creation, assessment, learning plan, lesson, confident voice transcription, completion report, persisted speaking time, and next-lesson adaptation. Tandem prompt generation remains private by construction.

## Tests

The Sprint suite covers profile validation, student isolation, adaptive assessment, certification disclaimer, curriculum selection, difficulty changes, plans, micro-lessons, hint ladder, lesson memory/progress, overcorrection, regression review, grammar uncertainty, guardian policy, low-confidence transcription, both track E2E pilots, Telegram-to-Education routing, and education-data deletion. Existing Telegram MVP regression tests remain in the full suite.

## Known Limitations

- Persistence is process-local; production requires an encrypted durable repository with row-level ownership enforcement and retention controls.
- The assessment scorer is deterministic scaffolding. Production language analysis requires validated rubrics and monitored model prompts.
- Speech recognition, speech synthesis, and pronunciation scoring are interfaces; deployment providers are not configured in this sprint.
- Telegram currently routes `/learn` and text onboarding/menu behavior; receiving binary voice messages and emitting voice replies requires an adapter extension.
- Curricula are deliberately small skeletons, not full accredited courses, and C1/C2 content is not yet populated.
- Grammar rules are a minimal curated registry. Unknown rules produce uncertainty instead of fabrication.
- Minor mode is preparation only and is not approval for public child access.
- Cost metric fields and provider instrumentation require production billing integrations.

## Recommendations for Sprint 024

Founder approval should precede any next sprint. Candidate follow-up work is durable scoped storage, audited provider selection, richer validated curriculum content, human-teacher review, Telegram voice-media transport, cost telemetry, and controlled real-user pilot instrumentation. Child access, monetization, full tandem exchange, exams, and Digital Human live lessons should remain gated behind dedicated product, privacy, and safety decisions.
