"""Orchestration engine for all Sprint 021 perception entry points."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .integrations import PerceptionIntegrations
from .models import (
    AssetReference, Confidence, MediaType, MultimodalBundle, Observation,
    PerceptionRequest, PerceptionResult, ProviderOutput,
)
from .router import MultimodalRouter
from .security import PerceptionGuardian


class PerceptionLimitError(RuntimeError):
    pass


class MultimodalPerceptionEngine:
    """Routes untrusted assets, normalizes observations, and preserves lineage."""

    def __init__(self, router: MultimodalRouter, guardian: PerceptionGuardian,
                 integrations: PerceptionIntegrations | None = None,
                 cost_limits: dict[str, float] | None = None) -> None:
        self.router = router
        self.guardian = guardian
        self.integrations = integrations or PerceptionIntegrations()
        self.cost_limits = cost_limits or {
            "vision": 10.0, "transcription": 10.0, "video_frames": 20.0,
            "document": 10.0,
        }

    def process(self, request: PerceptionRequest) -> PerceptionResult:
        if request.media_type == MediaType.MULTIMODAL_BUNDLE:
            bundle = request.context.get("bundle")
            if not isinstance(bundle, MultimodalBundle):
                raise ValueError("MULTIMODAL_BUNDLE request requires context['bundle']")
            return self.process_multimodal_bundle(bundle, request=request)
        if not request.asset_references and request.media_type != MediaType.TEXT:
            raise ValueError("media requests require at least one asset reference")

        provider = self.router.select(request)
        asset = request.asset_references[0] if request.asset_references else AssetReference(
            request.request_id, "inline:text", MediaType.TEXT
        )
        output, category = self._invoke(provider, request, asset)
        self._check_cost(category, output.cost)
        result = self._normalize(request, provider.name, output)
        result = self.guardian.inspect(result)
        self.integrations.publish(request, result)
        return result

    def _invoke(self, provider: Any, request: PerceptionRequest,
                asset: AssetReference) -> tuple[ProviderOutput, str]:
        media = request.media_type
        if media == MediaType.IMAGE:
            return provider.analyze_image(asset, request.context), "vision"
        if media in (MediaType.SCREENSHOT, MediaType.WEB_CAPTURE, MediaType.TOOL_OUTPUT):
            return provider.analyze_screenshot(asset, request.context), "vision"
        if media in (MediaType.AUDIO, MediaType.VOICE_MESSAGE):
            return provider.transcribe(asset), "transcription"
        if media == MediaType.VIDEO:
            return provider.analyze_frames(asset, request.context), "video_frames"
        if media in (MediaType.PDF, MediaType.DOCUMENT):
            return provider.analyze_document(asset, request.context), "document"
        if media == MediaType.TEXT:
            content = str(request.context.get("text", ""))
            kind, confidence, uncertainty = self.guardian.classify_content(content)
            return ProviderOutput(observations=({"type": kind, "content": content},),
                                  extracted_text=content, confidence=confidence,
                                  uncertainty=uncertainty), "document"
        raise NotImplementedError(media.value)

    def _normalize(self, request: PerceptionRequest, model: str,
                   output: ProviderOutput) -> PerceptionResult:
        default_source = request.asset_references[0].asset_id if request.asset_references else request.request_id
        refs = request.asset_references or (
            AssetReference(default_source, "inline:text", MediaType.TEXT),
        )
        allowed_sources = {item.asset_id for item in refs}
        observations = []
        uncertainty = list(output.uncertainty)
        for raw in output.observations:
            source_id = str(raw.get("source_id", default_source))
            if source_id not in allowed_sources:
                raise ValueError("provider returned an observation for an unknown source")
            content = str(raw.get("content", ""))
            kind = str(raw.get("type", "observation"))
            injection_kind, _, warning = self.guardian.classify_content(content)
            if injection_kind == "untrusted_embedded_instruction":
                kind = injection_kind
                uncertainty.extend(warning)
            confidence = raw.get("confidence", output.confidence)
            if not isinstance(confidence, Confidence):
                confidence = Confidence(str(confidence))
            observations.append(Observation(source_id, kind, content,
                                            raw.get("location"), confidence, model))
        return PerceptionResult(
            request_id=request.request_id, observations=tuple(observations),
            extracted_text=output.extracted_text, objects=tuple(output.objects),
            scenes=tuple(output.scenes), speech_transcript=output.transcript,
            speakers=tuple(output.speakers), timeline=tuple(output.timeline),
            confidence=output.confidence, uncertainty=tuple(dict.fromkeys(uncertainty)),
            model=model, source_references=tuple(refs), costs={"total": output.cost},
        )

    def _check_cost(self, category: str, cost: float) -> None:
        if cost < 0 or cost > self.cost_limits.get(category, 0):
            raise PerceptionLimitError(f"{category} cost {cost} exceeds configured limit")

    def process_text(self, text: str, **kwargs: Any) -> PerceptionResult:
        return self.process(self._request(MediaType.TEXT, (), context={"text": text}, **kwargs))

    def process_photo(self, asset: AssetReference, **kwargs: Any) -> PerceptionResult:
        media = MediaType.SCREENSHOT if kwargs.pop("screenshot", False) else MediaType.IMAGE
        return self.process(self._request(media, (asset,), **kwargs))

    def process_voice(self, asset: AssetReference, **kwargs: Any) -> PerceptionResult:
        return self.process(self._request(MediaType.VOICE_MESSAGE, (asset,), **kwargs))

    def process_video(self, asset: AssetReference, **kwargs: Any) -> PerceptionResult:
        return self.process(self._request(MediaType.VIDEO, (asset,), **kwargs))

    def process_document(self, asset: AssetReference, **kwargs: Any) -> PerceptionResult:
        media = MediaType.PDF if asset.media_type == MediaType.PDF else MediaType.DOCUMENT
        return self.process(self._request(media, (asset,), **kwargs))

    def process_multimodal_bundle(self, bundle: MultimodalBundle, *,
                                  request: PerceptionRequest | None = None,
                                  **kwargs: Any) -> PerceptionResult:
        base = request or self._request(MediaType.MULTIMODAL_BUNDLE, bundle.assets,
                                        context={"bundle": bundle}, **kwargs)
        results = []
        if bundle.text:
            text_asset = AssetReference(f"{bundle.bundle_id}_text", "inline:bundle-text", MediaType.TEXT)
            results.append(self.process(replace(base, media_type=MediaType.TEXT,
                                                asset_references=(text_asset,), context={"text": bundle.text})))
        for asset in bundle.assets:
            results.append(self.process(replace(base, media_type=asset.media_type,
                                                asset_references=(asset,), context={})))
        if not results:
            raise ValueError("multimodal bundle cannot be empty")
        merged = PerceptionResult(
            request_id=base.request_id,
            observations=tuple(obs for result in results for obs in result.observations),
            extracted_text="\n".join(filter(None, (r.extracted_text for r in results))),
            objects=tuple(item for r in results for item in r.objects),
            scenes=tuple(item for r in results for item in r.scenes),
            speech_transcript="\n".join(filter(None, (r.speech_transcript for r in results))),
            speakers=tuple(item for r in results for item in r.speakers),
            timeline=tuple(item for r in results for item in r.timeline),
            confidence=max((r.confidence for r in results), key=list(Confidence).index),
            uncertainty=tuple(item for r in results for item in r.uncertainty),
            model="multimodal:" + ",".join(dict.fromkeys(r.model for r in results)),
            source_references=tuple(asset for result in results for asset in result.source_references),
            costs={"total": sum(r.costs.get("total", 0) for r in results)},
        )
        return self.guardian.inspect(merged)

    @staticmethod
    def _request(media_type: MediaType, assets: tuple[AssetReference, ...], **kwargs: Any) -> PerceptionRequest:
        kwargs.setdefault("source", "telegram")
        kwargs.setdefault("user", "founder")
        return PerceptionRequest(media_type=media_type, asset_references=assets, **kwargs)
