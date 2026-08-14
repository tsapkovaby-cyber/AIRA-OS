# Sprint 034 — Voice Tutor

## Goal
Prepare multilingual spoken practice without coupling AIRA Academy to a paid speech vendor.

## Architecture
`VoiceTutorService` separates speech-to-text and text-to-speech behind ports. CI uses deterministic adapters and makes no external or paid calls. Target language (what the student practices) and explanation language (what AIRA uses for coaching and application UX) remain independent.

## AIRA voice profiles
- `aira-founder`: canonical production AIRA voice. Intended to represent the founder-authorized voice identity.
- `aira-fallback`: operational fallback.
- `aira-test`: deterministic CI/development voice.

The repository MUST NOT contain founder master recordings, cloned voice models, provider API keys, voice enrollment secrets, or biometric/source audio. A production provider adapter should receive a protected external voice-profile identifier from deployment secrets/configuration.

## Supported languages
English, Russian, Spanish, Italian, Turkish, Kazakh, French, and German use the multilingual catalog introduced in Sprint 033.

## Future production integration
A later deployment sprint may connect real STT/TTS providers, browser microphone capture, streaming playback, pronunciation metrics, and protected Founder Voice enrollment. Provider selection remains replaceable and should not change learning-domain contracts.
