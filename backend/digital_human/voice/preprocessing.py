from __future__ import annotations

from dataclasses import dataclass

from .domain import VoiceReference


@dataclass(frozen=True)
class AudioAnalysis:
    duration_seconds: float
    sample_rate: int
    channels: int
    silence_seconds: float
    clipping_events: int
    background_noise_db: float | None
    speech_to_noise_db: float | None
    usable_speech_seconds: float


class VoicePreprocessor:
    """Contract for analysis and non-destructive creation of technical children."""

    def analyze(self, source: VoiceReference) -> AudioAnalysis:
        raise NotImplementedError

    def convert(self, source: VoiceReference, *, output_id: str, output_format: str, sample_rate: int) -> VoiceReference:
        """Implementations must write a new file and return a child reference."""
        raise NotImplementedError
