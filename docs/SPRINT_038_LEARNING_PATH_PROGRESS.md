# Sprint 038 — Learning Path & Progress

Sprint 038 turns existing enrollment/progress primitives into a student-facing resumable learning path.

## Student experience

For an enrolled course the platform can project an ordered path containing every lesson with `completed`, `in_progress`, or `not_started` state, prerequisite-based lock state, estimated duration, completion percentage, and the current/next resumable lesson.

The projection is derived from the canonical `Enrollment` and `Course`; it does not create a competing progress store. Completing a lesson therefore immediately changes the path, and the authenticated API can feed the web dashboard from the same source of truth.

## Architecture

`backend.learning.path` is a read/projection layer. `LearningPlatformService.learning_path_snapshot()` owns domain access and `LearningPlatformAPI.learning_path()` exposes the authenticated representation. Existing `start_lesson`, `complete_lesson`, `progress`, memory, personalization, Voice Tutor, and Video Lessons remain reusable around the same lesson identifiers.

## Languages and plans

The path is language-neutral and works with all Academy course languages, including Korean and Mandarin Chinese added in Sprint 037. Entitlement enforcement from Sprint 036 remains a separate concern and can gate access without changing progress semantics.

## Next integration

The dashboard should render this snapshot as Continue Learning, progress percentage, lesson states, and resume actions. Future production persistence can store the existing enrollment state behind ports without changing this projection contract.
