from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from .domain import ProviderStatus, ProviderVoiceProfile, SpeechGenerationRequest


@dataclass(frozen=True)
class ProviderCapabilities:
    languages: tuple[str, ...]
    voice_reference: bool
    voice_clone: bool
    emotion: bool
    streaming: bool


@dataclass(frozen=True)
class SynthesisResult:
    audio: bytes
    spoken_text: str
    cost: float


class SpeechProvider(ABC):
    name: str

    @abstractmethod
    def synthesize(self, request: SpeechGenerationRequest, profile: ProviderVoiceProfile) -> SynthesisResult: ...

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities: ...

    @abstractmethod
    def estimate_cost(self, request: SpeechGenerationRequest) -> float: ...

    @abstractmethod
    def health_check(self) -> bool: ...

    def supports_voice_reference(self) -> bool: return self.get_capabilities().voice_reference
    def supports_voice_clone(self) -> bool: return self.get_capabilities().voice_clone
    def supports_emotion(self) -> bool: return self.get_capabilities().emotion
    def supports_streaming(self) -> bool: return self.get_capabilities().streaming


@dataclass(frozen=True)
class RoutingCandidate:
    provider: SpeechProvider
    profile: ProviderVoiceProfile
    voice_similarity: float
    russian_quality: float
    english_quality: float
    emotion_control: float
    latency: float
    privacy: float
    long_form_stability: float
    commercial_suitability: float


class VoiceRouter:
    """Selects only policy-approved, compatible providers using identity first."""

    def route(self, request: SpeechGenerationRequest, candidates: Iterable[RoutingCandidate]) -> RoutingCandidate:
        eligible = [c for c in candidates if c.profile.status is ProviderStatus.APPROVED and c.provider.health_check()
                    and request.language in c.provider.get_capabilities().languages]
        if not eligible:
            raise PermissionError("DENIED: no approved compatible voice provider")
        return max(eligible, key=lambda c: (c.voice_similarity, self._quality(c, request), -c.provider.estimate_cost(request)))

    @staticmethod
    def _quality(candidate: RoutingCandidate, request: SpeechGenerationRequest) -> float:
        language = candidate.russian_quality if request.language == "ru" else candidate.english_quality
        return language + candidate.emotion_control + candidate.privacy + candidate.long_form_stability + candidate.commercial_suitability - candidate.latency
