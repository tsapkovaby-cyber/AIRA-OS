"""Adaptive classroom policy with explicit, pedagogical signals only."""

from dataclasses import dataclass


LEVEL_RATIO = {"A0": 0.70, "A1": 0.70, "A2": 0.78, "B1": 0.90, "B2": 0.95, "C1": 1.0, "C2": 1.0}


@dataclass(slots=True)
class ConversationPolicy:
    level: str
    target_language_ratio: float = 0.7
    difficulty: int = 1
    speech_speed: float = 0.9
    maximum_sentences: int = 3
    correction_frequency_turns: int = 3

    def __post_init__(self) -> None:
        self.target_language_ratio = LEVEL_RATIO.get(self.level.upper(), 0.8)
        self.difficulty = max(1, min(5, (list(LEVEL_RATIO).index(self.level.upper()) // 2) + 1)) if self.level.upper() in LEVEL_RATIO else 2
        self.speech_speed = 0.85 if self.target_language_ratio <= 0.7 else 1.0

    def adapt(self, *, struggle: bool = False, success_streak: int = 0, requested_speed: float | None = None) -> None:
        if struggle:
            self.difficulty = max(1, self.difficulty - 1)
            self.target_language_ratio = max(0.7, self.target_language_ratio - 0.1)
            self.speech_speed = max(0.65, self.speech_speed - 0.1)
        elif success_streak >= 3:
            self.difficulty = min(5, self.difficulty + 1)
            self.target_language_ratio = min(1.0, self.target_language_ratio + 0.05)
        if requested_speed is not None:
            self.speech_speed = min(1.25, max(0.5, requested_speed))

    def constrain_response(self, text: str) -> str:
        chunks = [part.strip() for part in text.replace("!", "!|").replace("?", "?|").replace(".", ".|").split("|") if part.strip()]
        return " ".join(chunks[: self.maximum_sentences])
