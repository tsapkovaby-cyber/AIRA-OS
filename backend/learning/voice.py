"""Provider-neutral voice tutoring primitives for AIRA Academy.

No founder audio or provider credentials belong in the repository. Production
adapters receive only a protected voice-profile identifier from deployment
configuration; CI uses deterministic local adapters below.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .languages import get_language

@dataclass(frozen=True, slots=True)
class VoiceProfile:
    id: str
    label: str
    kind: str

FOUNDER_VOICE = VoiceProfile("aira-founder", "AIRA Founder Voice", "founder")
FALLBACK_VOICE = VoiceProfile("aira-fallback", "AIRA Fallback Voice", "fallback")
TEST_VOICE = VoiceProfile("aira-test", "AIRA Test Voice", "test")

@dataclass(slots=True)
class VoiceTurn:
    student_id: str
    target_language: str
    explanation_language: str
    transcript: str
    tutor_text: str
    voice_profile_id: str
    audio_reference: str | None = None

class SpeechToTextPort(Protocol):
    def transcribe(self, audio: bytes, *, language: str) -> str: ...

class TextToSpeechPort(Protocol):
    def synthesize(self, text: str, *, language: str, voice_profile_id: str) -> str: ...

class DeterministicSpeechToText:
    def transcribe(self, audio: bytes, *, language: str) -> str:
        get_language(language)
        return audio.decode("utf-8").strip()

class DeterministicTextToSpeech:
    def synthesize(self, text: str, *, language: str, voice_profile_id: str) -> str:
        get_language(language)
        return f"test-audio://{voice_profile_id}/{language}/{len(text)}"

class VoiceTutorService:
    def __init__(self, *, stt: SpeechToTextPort | None = None, tts: TextToSpeechPort | None = None, production_voice: VoiceProfile = FOUNDER_VOICE) -> None:
        self.stt = stt or DeterministicSpeechToText()
        self.tts = tts or DeterministicTextToSpeech()
        self.production_voice = production_voice

    def practice_turn(self, *, student_id: str, audio: bytes, target_language: str, explanation_language: str, test_mode: bool = True) -> VoiceTurn:
        target = get_language(target_language)
        explanation = get_language(explanation_language)
        transcript = self.stt.transcribe(audio, language=target.code)
        tutor_text = self._feedback(transcript, target.name, explanation.name)
        profile = TEST_VOICE if test_mode else self.production_voice
        audio_reference = self.tts.synthesize(tutor_text, language=explanation.code, voice_profile_id=profile.id)
        return VoiceTurn(student_id, target.name, explanation.name, transcript, tutor_text, profile.id, audio_reference)

    @staticmethod
    def _feedback(transcript: str, target_language: str, explanation_language: str) -> str:
        if not transcript:
            return f"No speech detected. Explain the retry in {explanation_language}."
        return f"Practice {target_language}: '{transcript}'. Give concise coaching in {explanation_language}, then continue the dialogue."
