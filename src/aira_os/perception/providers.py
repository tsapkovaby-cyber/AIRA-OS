"""Abstract multimodal providers. Implementations never receive unapproved assets."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence

from .models import AssetReference, ProviderOutput


class VisionProvider(ABC):
    name: str

    @abstractmethod
    def analyze_image(self, asset: AssetReference, context: Mapping[str, Any]) -> ProviderOutput: ...

    @abstractmethod
    def analyze_frames(self, asset: AssetReference, context: Mapping[str, Any]) -> ProviderOutput: ...

    @abstractmethod
    def analyze_screenshot(self, asset: AssetReference, context: Mapping[str, Any]) -> ProviderOutput: ...

    @abstractmethod
    def compare_images(self, assets: Sequence[AssetReference], context: Mapping[str, Any]) -> ProviderOutput: ...

    @abstractmethod
    def get_capabilities(self) -> frozenset[str]: ...


class SpeechRecognitionProvider(ABC):
    name: str

    @abstractmethod
    def transcribe(self, asset: AssetReference) -> ProviderOutput: ...

    @abstractmethod
    def detect_language(self, asset: AssetReference) -> str: ...

    @abstractmethod
    def get_timestamps(self, asset: AssetReference) -> ProviderOutput: ...

    @abstractmethod
    def estimate_cost(self, asset: AssetReference) -> float: ...


class TextExtractionProvider(ABC):
    name: str

    @abstractmethod
    def extract(self, asset: AssetReference) -> ProviderOutput: ...


class DocumentProvider(ABC):
    name: str

    @abstractmethod
    def analyze_document(self, asset: AssetReference, context: Mapping[str, Any]) -> ProviderOutput: ...
