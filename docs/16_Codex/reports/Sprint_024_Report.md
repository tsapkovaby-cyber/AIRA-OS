# Sprint 024 Report — AIRA Live Language Classroom

## Summary

Implemented the Sprint 024 MVP as a Python, transport-independent classroom for RU → EN and EN → RU. Conversation remains short and natural; corrections are selective and delayed by default. No Sprint 025 work was started.

## Live Classroom Architecture

The domain defines sessions, turns, lifecycle states, modes, pronunciation targets, skill mastery, speaking-confidence learning signals, and cost totals. Ports isolate ASR, TTS, conversation, transport, and memory. The controller composes them and protects event idempotency.

## Voice Pipeline

Telegram voice enters ASR, passes a 0.70 confidence gate, is analyzed, answered, synthesized with an AIRA canonical profile, and returned as voice. TTS failures and voice-limit exhaustion fall back to text. Streaming and interruption remain provider-dependent future capabilities.

## Conversation Controller

The controller starts supported duration profiles, processes turns, applies response constraints and explicit slow commands, buffers corrections, records learning artifacts, generates summaries, and completes sessions. Duplicate update IDs return the original turn.

## Correction Strategy

Corrections rank meaning-breaking, repeated, lesson-target, frequent, pronunciation, and style issues. The default checkpoint is every third student turn and emits at most one correction. Low-confidence transcription produces confirmation, never a learner mistake.

## Adaptive Learning

CEFR levels seed difficulty, target/support ratio, and speed. Struggle signals simplify without lowering beginners below 70% target language; successful streaks increase challenge gradually. No medical or psychological inference is performed.

## Pronunciation

The pronunciation target model and dedicated conversational prompt support demonstration, repeat, feedback, retry, contrast and mastery tracking. Provider-grade phoneme scoring remains an adapter integration.

## Listening

Listening mode emits a short clean prompt and comprehension question. Multi-speaker audio, noise, accent variation, and shadowing timing remain future provider work.

## Roleplay

Roleplay uses a scenario supplied to the session and produces in-role prompts. The port boundary is ready to connect Sprint 023’s production scenario engine.

## Telegram Experience

`TelegramVoiceTransport` supports voice with a small optional correction caption and text fallback. Fast-mode messages are capped at three sentences. The included transport is deterministic; deployment should bind it to the existing Telegram client.

## RU → EN Pilot

The automated pilot runs three English turns from a Russian-speaking A1 learner, verifies conversation continues before the buffered `want to go` correction, completes the session, and retrieves the summary.

## EN → RU Pilot

The automated pilot runs a Russian food conversation, verifies a Russian continuation, persists its summary, and proves another student cannot retrieve it.

## Latency

The controller performs one provider pass per stage and avoids unnecessary retries. Actual latency depends on ASR, model, TTS, and Telegram; zero latency is not promised. Full duplex streaming is not in the MVP.

## Cost

Sessions expose ASR, LLM, TTS, pronunciation, total cost, maximum cost, duration, and voice-generation limits. Production adapters must populate provider charges and enforce approved downgrade routing; the MVP enforces the voice-turn limit.

## Privacy

Audio bytes are not saved to learning memory. References require explicit input from an approved retention layer. Summaries are isolated by student ID. The design prohibits automatic training use, unrestricted retention, certification claims, diagnosis, and a replacement AIRA persona.

## Tests

The suite covers model creation, detection, correction priority/frequency, ratios, adaptation, speed, transcript uncertainty, mode prompts, summaries, transport fallback, canonical voice, idempotency, both language pilots, and memory isolation.

## Known Limitations

- Provider adapters are deterministic local MVPs; production ASR/TTS/LLM and Telegram API bindings are deployment work.
- Speaking duration and monetary cost require timestamps/usage returned by production providers.
- Pronunciation scoring is modeled but needs a phoneme-aware provider.
- Streaming, barge-in, WebRTC, live tandem observation, and minor mode are not implemented.
- The production Sprint 023 scenario and learning-memory stores were absent from this repository, so clean ports are supplied for integration.

## Recommendations for Sprint 025

Only after Founder approval: bind production providers with measured latency/cost, add encrypted retention jobs and deletion APIs, integrate the Sprint 023 scenario/memory implementations, and pilot streaming endpoint detection. Do not start these changes automatically.
