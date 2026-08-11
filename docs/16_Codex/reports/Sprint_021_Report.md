# Sprint 021 Report — Multimodal Perception & Understanding Engine

**Sprint:** S021  
**Version:** 1.0  
**Status:** Implemented  
**Scope boundary:** Sprint 021 only; no Sprint 022 behavior is implemented.

## Summary

Sprint 021 introduces AIRA's provider-neutral perception domain. The engine accepts
text, image, screenshot, audio, voice-message, video, PDF/document, web-capture,
tool-output, and multimodal-bundle requests. It routes only to privacy-approved
providers, returns structured observations, retains source lineage and uncertainty,
tracks costs, and emits review-required candidates to downstream systems.

Perception output is an **observation**, not automatically a verified fact. Media is
always untrusted data and never an instruction channel.

## Architecture

The implementation is split into:

1. `models.py`: immutable requests, results, observations, timelines, assets, and bundles.
2. `providers.py`: abstract contracts for vision, speech recognition, OCR, and documents.
3. `router.py`: task-, media-, privacy-, cost-, latency-, and accuracy-aware selection.
4. `security.py`: Guardian privacy authorization, lineage validation, and injection labeling.
5. `engine.py`: dispatch, normalization, cost limits, bundle aggregation, and Telegram-ready APIs.
6. `integrations.py`: review-gated reasoning, knowledge, memory, and experiment candidates.

The lineage path is upload/source → asset reference → request → observation/result →
candidate. An observation includes its source ID, location where supplied, provider
model, confidence, and creation time. Results retain the complete asset references.

## Image Perception

`VisionProvider.analyze_image()` supports provider-defined scene understanding, object
recognition, visible text, quality, composition, artifact, content, and identity analysis.
`compare_images()` supports identity continuity and self-inspection workflows. The engine
normalizes provider output without inventing absent objects or claims.

Generated images of AIRA can use the `aira_image_review` or `aira_identity_review` task
profiles. Identity and quality conclusions remain observations for Guardian/founder review.

## Audio Perception

`SpeechRecognitionProvider` exposes transcription, language detection, timestamps, and
cost estimation. Voice messages use a dedicated media type and Telegram-ready handler.
A founder recording is transcribed for command understanding but is not automatically
submitted to canonical voice memory or a voice dataset.

## Video Perception

Video dispatch calls frame analysis and accepts synchronized transcript, scene, object,
and `TimelineEntry` outputs. Entries carry start/end seconds, content, source, and
confidence. Providers can therefore combine frame, speech, motion, quality, and identity
continuity review for the Sprint 020 Guardian hand-off.

## Document Perception

PDF and extracted document content use the document-provider contract. Providers may
return titles, sections, claims-as-observations, tables, dates, sources, and action items,
with page or section locations. `TextExtractionProvider` separately abstracts OCR while
the original visual asset remains referenced by the result.

## Multimodal Bundles

`MultimodalBundle` contains assets, optional text, and validated source relationships.
The engine processes each modality through the same privacy and Guardian boundaries and
aggregates observations, transcripts, timelines, uncertainty, sources, models, and cost.
Relationships referencing assets outside the bundle are rejected.

## Provider Layer

Provider selection filters registrations by media type, task profile, and privacy level,
then honors cost, latency, or accuracy policy. Supported profiles are:

- `aira_image_review`
- `aira_video_review`
- `aira_tool_screenshot`
- `aira_document_analysis`
- `aira_voice_message`
- `aira_content_review`
- `aira_identity_review`
- `aira_experiment_evidence`

Provider implementations are deliberately outside this sprint's core, permitting local
or hosted backends without coupling domain models to a vendor.

## Privacy

Privacy levels are `PUBLIC`, `INTERNAL`, `PRIVATE`, and `RESTRICTED`. A provider must pass
both router eligibility and Guardian authorization for the exact level. No fallback can
silently weaken privacy. Deployments should approve only audited providers and storage
paths, with local-only providers for restricted inputs where policy requires.

## Security

- Documents, screenshots, web captures, transcripts, and tool output are untrusted data.
- Common embedded instruction patterns are relabeled `untrusted_embedded_instruction`.
- Such text is retained for provenance, surfaced as uncertainty, and never dispatched.
- Unknown provider source IDs and missing result lineage are rejected.
- Unapproved providers and excessive per-operation costs fail closed.
- Confidence remains explicit; results do not promote observations to facts.

## Knowledge, Memory, Experiment, and Reasoning Integration

Downstream connections produce `PerceptionCandidate` records rather than direct writes.
Every candidate preserves request/result/source IDs and sets
`requires_guardian_review=True`. Knowledge and memory submission must be explicitly
requested by context and remains subject to their policies. An experiment ID enables an
experiment-evidence candidate. Reasoning receives a candidate only when a configured sink
exists. This prevents observation-to-fact and recording-to-memory promotion by default.

## Telegram Readiness

`MultimodalPerceptionEngine` exposes `process_text()`, `process_photo()`,
`process_voice()`, `process_video()`, `process_document()`, and
`process_multimodal_bundle()`. Defaults label these calls as Telegram/founder-originated,
while callers can supply privacy, purpose, requested analyses, context, and model policy.
These are transport-independent interfaces for Sprint 022 to consume; this sprint does
not implement a Telegram bot or authorize UI actions.

## Tests

The suite covers image and screenshot normalization, OCR-like visible text, voice
transcription, video timelines, document injection resistance, uncertainty, source
linking, privacy authorization, multimodal relationships, cost limits, review-gated
integrations, and every Telegram-compatible media handler represented by those paths.

## Known Limitations

- No production model/provider adapter or binary asset storage is bundled.
- Providers, not the orchestration layer, determine actual recognition quality.
- Composite video providers must synchronize frame and speech analysis themselves.
- DOC-like files require upstream extraction or an appropriate provider implementation.
- Injection detection is defense-in-depth labeling, not a substitute for keeping model
  output out of privileged instruction channels.
- Verification of public factual claims remains a Research/Knowledge responsibility.

## Recommendations for Sprint 022

1. Map Telegram upload IDs to durable, checksummed `AssetReference` objects before calls.
2. Assign privacy at ingestion and configure an explicit provider allowlist per level.
3. Preserve message, reply, album, and bundle relationships in transport metadata.
4. Apply file size, duration, MIME validation, malware scanning, and rate limits first.
5. Present uncertainty and source references in responses without implying fact status.
6. Require explicit consent before any voice recording can enter voice-dataset workflows.
7. Add production provider contract tests, telemetry, deletion, and retention controls.

Sprint 021 is complete. **STOP: await Founder approval before beginning Sprint 022.**
