from dataclasses import dataclass

from .catalog import VOICE_BENCHMARK_SCENARIOS
from .domain import VOICE_BENCHMARK_ID


@dataclass(frozen=True)
class VoiceBenchmark:
    benchmark_id: str = VOICE_BENCHMARK_ID
    scenarios: tuple[str, ...] = VOICE_BENCHMARK_SCENARIOS
    metrics: tuple[str, ...] = (
        "voice_identity", "naturalness", "russian_pronunciation", "english_terms",
        "emotional_control", "long_form_stability", "latency", "cost", "api_quality",
        "privacy", "commercial_suitability",
    )
    founder_evaluation_required: bool = True
