# AIRA Motion, Video & Lip-Sync Engine

## Boundary and pipeline

Providers render AIRA; they never define the character. `AIRA_DIGITAL_HUMAN_V1` composes the existing core, visual and voice identity versions with separately versioned motion, expression, lip-sync and behavior profiles. No canonical face or voice is created or modified by this engine.

The controlled pipeline is: approved script → approved voice asset → motion plan → video base → lip sync → temporal identity/audio-video evaluation → Guardian → Founder review. Publication requires both approvals. Raw and canonical assets are immutable; every edit creates a child `VideoAsset`.

Short form defaults to 9:16, 15–60 seconds, stable eye contact and subtle gestures. Long form uses stable, separately evaluated segments, B-roll and voiceover rather than assuming a generator can maintain identity for ten minutes.

## Domain and evaluation

The Python package supplies `MotionProfile`, `BlinkProfile`, `ExpressionProfile`, `LipSyncProfile`, `SceneProfile`, `CameraProfile`, `VideoGenerationRequest`, `VideoAsset`, `VideoSegment`, `VideoProject`, disclosure and feedback records. Scores for identity, temporal identity, motion, lip sync, quality and brand remain separate.

Temporal evaluation checks all supplied first/middle/final/random/critical frames, records timeline drift artifacts, and cannot hide a local identity collapse behind an average. Lip-sync checks timing, phonemes, pauses, jaw, lip shape, face preservation and delay. Motion checks naturalness, continuity, eyes and hands.

## Providers, security and cost

Video, motion and lip-sync contracts are independent and composable. Routing requires an allowlisted provider, declared capabilities, health, reference authorization and budget fit, then weights identity and privacy most heavily. Canonical references require provider research approval and explicit Founder approval. Versioned benchmark results must name provider/model/API/test date externally so regressions remain comparable.

Budget controls cover per-video, daily and monthly spend; exceeding a limit produces `WAITING_FOUNDER_APPROVAL`. Storage keeps references, hashes, lineage, scores and metadata while large bytes remain in the asset-store abstraction.

## Benchmark

`AIRA_VIDEO_BENCHMARK_V1` defines twelve scenarios covering talking, expression, turns, hands, workspace, walking, camera movement, long speech, Russian/English lip sync, hair and 30-second stability. Metrics cover identity, temporal identity, synchronization, motion/expression, eyes/hands/hair/clothing, camera/prompt adherence, cost and latency.

## Privacy and limitations

Motion is designed for AIRA and never inferred as a sensitive Founder characteristic. The output represents AIRA, not the Founder. Real-time avatars, live calls, unrestricted face replacement, autonomous publication, motion capture and cinematic/3D systems remain out of scope. Actual provider adapters, media decoding, frame sampling and dashboard/Telegram clients require approved infrastructure in later work.
