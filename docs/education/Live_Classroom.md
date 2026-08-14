# Live Classroom

Sprint 024 provides an asynchronous, near-real-time voice classroom whose education logic is independent of Telegram. `LiveClassroomController` owns the lifecycle, invokes ASR, analysis, conversation and canonical TTS ports, and persists only a learning summary. The MVP uses short utterance chunks; provider latency means it does not promise zero latency.

Supported initial tracks are RU → EN and EN → RU. Modes include free/guided conversation, roleplay, pronunciation, listening, vocabulary, grammar in context, exam speaking, tandem preparation and fluency. Sessions use explicit terminal states and 5–60 minute profiles. Provider adapters can later implement partial ASR and streaming TTS without changing education policy.

Failures degrade from voice to text, duplicate transport event IDs are idempotent, and uncertain transcripts request confirmation instead of producing learner errors.
