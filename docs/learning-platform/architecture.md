# AIRA Learning Platform Architecture

AIRA Learning Platform is a user-facing education domain on top of AIRA OS. `backend/learning` owns deterministic student/course/progress rules. Telegram, HTTP, Railway and AI providers remain adapters.

Before creating this canonical package, the integrated repository was reviewed for existing education code. The earlier Academy and Live Classroom modules remain capabilities/reference implementations; Sprint 025 does not replace or activate them. `backend/learning` is the new application-domain boundary that future platform transports should call.

The platform reuses AIRA capabilities rather than duplicating them: the `LearningMemoryPort` is the boundary to AIRA Memory; `TutorPort` is the boundary to Intelligence/Voice/Perception. Sprint 025 ships in-memory/fake adapters so tests and core learning flows require no paid API.

Canonical hierarchy: Student → LearningProfile → Enrollment → Course → Module → Lesson → Exercise. Ownership is student-scoped at the application service boundary.
