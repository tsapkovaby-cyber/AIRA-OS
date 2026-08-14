"""Pluggable embedding contracts and deterministic development provider."""
from __future__ import annotations
from abc import ABC, abstractmethod
import hashlib, math, re


class EmbeddingProvider(ABC):
    version = "unknown"
    @abstractmethod
    def embed_text(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]
    @abstractmethod
    def health_check(self) -> bool: ...
    @abstractmethod
    def estimate_cost(self, texts: list[str]) -> float: ...


class MockEmbeddingProvider(EmbeddingProvider):
    """Stable hashed bag-of-words vectors; suitable for tests, never production."""
    version = "mock-hash-v1"
    def __init__(self, dimensions: int = 64): self.dimensions = dimensions
    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"\w+", text.casefold()):
            digest = hashlib.sha256(token.encode()).digest()
            vector[int.from_bytes(digest[:4], "big") % self.dimensions] += 1
        norm = math.sqrt(sum(value * value for value in vector)) or 1
        return [value / norm for value in vector]
    def health_check(self) -> bool: return True
    def estimate_cost(self, texts: list[str]) -> float: return 0.0

