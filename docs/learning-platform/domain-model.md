# Learning Domain Model

`Student` intentionally contains only a stable ID and timestamp. `LearningProfile` carries optional learning preferences and language metadata without making language mandatory for every future subject.

`Course` contains ordered modules and lessons. Lessons declare prerequisites and exercises. `Enrollment` owns per-student lifecycle state. `ExerciseResult` records normalized scores. `CourseProgress` is derived rather than trusted as independent state.

Tutor sessions and learning memory are accessed through ports so OpenAI, Telegram, voice and persistence implementations can change without changing learning-domain rules.
