# Voice Lessons

The MVP pipeline is audio capture → ASR → confidence gate → language analysis → conversation engine → canonical TTS → transport. `SpeechRecognizer` and `SpeechSynthesizer` are provider ports. `TurnDetector` supports silence, explicit stop, and provider endpoint signals.

All speech uses `AIRA_VOICE_IDENTITY_V1` or its English/Russian teacher profiles. These profiles are one canonical AIRA identity, not new personas. Telegram receives a short voice answer and an optional correction caption. TTS or voice-budget failure sends the response as text, preserving the lesson.

Future web/mobile/WebRTC transports can add partial transcripts, interruption, and streaming without embedding Telegram concerns in the controller.
