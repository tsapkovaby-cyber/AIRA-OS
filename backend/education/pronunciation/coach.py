from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class PronunciationResult:
    confidence: float
    clarity: float | None = None
    target_sounds: dict[str, float] = field(default_factory=dict)
    word_stress: dict[str, float] = field(default_factory=dict)
    feedback: list[str] = field(default_factory=list)


class PronunciationAnalyzer(Protocol):
    async def analyze(self, audio: bytes, target_text: str, language: str) -> PronunciationResult: ...


class PronunciationCoach:
    def __init__(self, analyzer: PronunciationAnalyzer | None = None):
        self.analyzer = analyzer

    async def analyze(self, audio: bytes, target_text: str, language: str) -> PronunciationResult:
        if not self.analyzer:
            return PronunciationResult(0, feedback=["Pronunciation analysis is not available for this recording."])
        return await self.analyzer.analyze(audio, target_text, language)

    @staticmethod
    def actionable(sound: str) -> str:
        if sound == "/θ/":
            return "Try /θ/ again: put your tongue lightly between your teeth and let air pass."
        return f"Try {sound} again slowly, then use it in the whole word."
