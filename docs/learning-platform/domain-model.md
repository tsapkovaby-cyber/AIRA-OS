# Learning Domain Model

`Student` intentionally contains only a stable ID and timestamp. `LearningProfile` carries optional learning preferences and language metadata without making language mandatory for every future subject. `LearningGoal` and `StudentPreference` provide typed extension points for richer profile services.

`Course` contains ordered modules and lessons. Lessons declare prerequisites and exercises. `Assessment` groups exercises for later assessment workflows. `Enrollment` owns per-student lifecycle state and learning-streak metadata. `LessonProgress` and `ExerciseResult` describe granular progress; `CourseProgress` is derived rather than trusted as independent state. `LearningPath` is a student-scoped deterministic view of currently available lessons.

Tutor sessions and learning memory are accessed through ports so OpenAI, Telegram, voice and persistence implementations can change without changing learning-domain rules.
