# Classroom Voice Privacy

Learner voice is personal data. Audio is processed temporarily and is not training data. The controller retains no audio bytes after a turn. A raw-audio reference is stored only when an approved storage layer explicitly supplies one under a configured retention policy; deployments should default to delete-after-transcription.

Providers must meet the deployment privacy policy. Storage is student-isolated and minimal, export/deletion controls belong at the persistence boundary, and tandem observation requires explicit consent. Public minor mode, unrestricted retention, emotional profiling, and medical speech diagnosis are out of scope.
