# Sprint 020 Report — Motion, Video & Lip-Sync Engine

## Summary

Sprint 020 introduces a provider-neutral, explainable digital-human video domain without redesigning AIRA's existing face, voice, personality or Constitution. The implementation treats providers as replaceable renderers and preserves Founder authority.

## Motion Architecture

`MotionProfile` versions calm body/head/gesture/eye/posture behavior, motion modes, expression coupling, approval history and a perceptual `BlinkProfile`. Motion scoring retains naturalness, temporal/body continuity, eyes and hands as inspectable inputs.

## Expression System

Nine initial expression names and bounded intensity are modeled with explicit facial, eye, brow and mouth behavior and compatible motion modes. The video identity lock limits expression intensity.

## Lip-Sync Architecture

`LipSyncProfile` pins voice version, language, phoneme model/provider/method, timing offset, quality threshold, identity safety and approval. A separate provider contract and evaluator expose timing, phoneme/pause match, jaw, lip shape, face preservation and audio/visual delay failures. Exact normalized transcript comparison prevents silent wording changes.

## Video Architecture

Requests bind approved script/speech, visual and voice versions, motion/expression/scene/camera/platform profiles, references, provider policy, duration, aspect ratio and cost. Assets retain distinct safety/quality scores, status, artifact evidence, hashes and immutable parent-child lineage. Ordered projects and segments support talking head, B-roll, screen demo and long-form composition.

## Provider Layer

Abstract video, motion and lip-sync contracts allow composition. The router gates on allowlist, health, capability, master-reference approval and budget, then prioritizes identity, privacy, synchronization and motion. Concrete external adapters are deliberately absent until reviewed.

## Video Identity Lock and Temporal Identity Evaluation

The lock pins both identity versions, permitted motion, expression/lip-sync limits, a minimum frame score and maximum timeline drop. Evaluation accepts sampled frame scores, flags each threshold/drop event with a timestamp/frame range and deliberately caps the temporal result so averages cannot conceal local collapse.

## Video Benchmark

`AIRA_VIDEO_BENCHMARK_V1` contains all twelve planned scenarios and fourteen separate metrics. Provider experiment persistence remains an integration point for the existing Experiment Engine: reports must retain provider/model/API/test and benchmark versions.

## Artifact Detection Model

The domain represents face/body/hand/hair/clothing/background/object/lip/eye/teeth/flicker/identity artifacts. Automated pixel/media detectors are adapter work; this sprint implements evidence records and Guardian consumption boundaries.

## Founder Feedback

Structured feedback preserves motion and lip-sync categories. A Founder motion rejection produces `REJECTED_MOTION_IDENTITY` even when automated scores are high. Publication requires approved asset state plus Guardian and Founder approvals.

## Security Review

Canonical reference upload requires both an approved provider and Founder authorization. Routers exclude unauthorized providers, raw assets are never overwritten, failed evidence remains available, motion is separately designed rather than inferred from the Founder, and output is explicitly AIRA—not the Founder.

## Cost Controls

Per-video, daily and monthly limits return `WAITING_FOUNDER_APPROVAL` before spend. Request-level provider estimates are also gated. Voice, upscale, edit, experiment and approved-minute accounting can extend the ledger when those pipelines exist.

## Digital Human Integration

`DigitalHumanProfile` composes existing core/visual/voice versions with motion, expression, lip-sync and behavior versions as `AIRA_DIGITAL_HUMAN_V1`. Guardian contracts integrate temporal identity, motion, lip-sync, transcript and voice checks without collapsing their scores.

## Tests and Test Results

The suite covers profile/request validation, frame drift, deliberate AV offset, routing/reference/budget denial, lineage, project ordering, wrong-face/wrong-voice/changed-transcript rejection, Founder override, publication gating, security, budget and benchmark definition. `python -m pytest` passes locally (11 tests).

## Known Limitations

No provider network calls, master uploads, live rendering, media decoding, biometric model, dashboard, Telegram client or automatic publishing is included. Frame sampling and visual/audio inference require approved model adapters and asset-storage infrastructure. Rights/music and editing metadata are documented policy boundaries rather than media processors.

## Technical Debt

Persist domain records in the repository's future database abstraction; connect provider outcomes to the Sprint 017 experiment store; add exact upstream visual/voice object adapters when their schemas enter this repository; add asynchronous job orchestration and storage lifecycle hooks; and calibrate thresholds with Founder-reviewed benchmark evidence.

## Recommendations for Sprint 021

Do not begin Sprint 021 without Founder approval. After approval, prioritize a sandboxed fake-provider end-to-end job runner and persistence adapters before evaluating any external provider. Establish consent/privacy records and a benchmark dataset before a controlled master-reference test.
