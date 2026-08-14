"""Isolated provider contracts and deterministic policy router."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from .models import ProviderCapability, VideoGenerationRequest

class VideoGenerationProvider(ABC):
    @abstractmethod
    def generate_video(self, request: VideoGenerationRequest) -> Any: ...
    def animate_reference(self, request): raise NotImplementedError
    def image_to_video(self, request): raise NotImplementedError
    def text_to_video(self, request): raise NotImplementedError
    def extend_video(self, asset_id: str, seconds: float): raise NotImplementedError
    @abstractmethod
    def get_capabilities(self) -> frozenset[ProviderCapability]: ...
    @abstractmethod
    def estimate_cost(self, request: VideoGenerationRequest) -> float: ...
    @abstractmethod
    def health_check(self) -> bool: ...

class MotionProvider(ABC):
    @abstractmethod
    def create_motion(self, motion_profile, duration_seconds: float): ...

class LipSyncProvider(ABC):
    @abstractmethod
    def synchronize(self, video_asset, speech_asset, profile): ...

@dataclass(frozen=True)
class ProviderRecord:
    name: str; provider: VideoGenerationProvider; approved_for_master_assets: bool
    identity_consistency: float; lipsync_quality: float; motion_naturalness: float
    latency_score: float; privacy_score: float; commercial_suitability: float

class VideoProviderRouter:
    def __init__(self, records: list[ProviderRecord]): self.records = records
    def route(self, request: VideoGenerationRequest, required: set[ProviderCapability]) -> ProviderRecord:
        candidates=[]
        for record in self.records:
            if record.name not in request.provider_policy or not record.provider.health_check(): continue
            if not required.issubset(record.provider.get_capabilities()): continue
            if request.reference_assets and not record.approved_for_master_assets: continue
            cost=record.provider.estimate_cost(request)
            if cost > request.cost_limit: continue
            rank=(record.identity_consistency*3 + record.lipsync_quality*2 + record.motion_naturalness*2
                  + record.privacy_score*2 + record.commercial_suitability + record.latency_score - cost)
            candidates.append((rank, record))
        if not candidates: raise LookupError("no approved provider satisfies identity, capability and budget policy")
        return max(candidates, key=lambda item: item[0])[1]
