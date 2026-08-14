"""Provider routing abstraction. Concrete credential-bearing adapters are out of scope."""

from .domain import ModelProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}

    def register(self, provider: ModelProvider) -> None:
        if provider.provider_id in self._providers:
            raise ValueError("duplicate provider")
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> ModelProvider:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise RuntimeError(f"provider unavailable: {provider_id}") from exc
