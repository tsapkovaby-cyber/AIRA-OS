# Sprint 018 Report — Visual Identity & Digital Human Engine

## Summary

Implemented the provider-independent domain and orchestration foundation for one stable AIRA across variable scenes, wardrobe, cameras and platforms. No visual was generated and no canonical appearance was redesigned.

## Canonical Identity and Master Reference Registration

`AIRA_MASTER_REFERENCE_V1` is registered as immutable Founder-approved Asset Storage metadata. Its protected URI and hash must be supplied by deployment; binaries do not live in ordinary database fields. `AIRA_VISUAL_IDENTITY_PACK_V1` includes structured face, blonde hair, critical blue-eye, natural light-skin, makeup, brand, wardrobe, variation and prompt policies while keeping the reference authoritative.

## Identity Profile, Hierarchy and Lock

Added validated identity/status objects, four-level reference hierarchy, a single-ACTIVE invariant, Founder-only promotion, immutable master protection and identity locks covering references, face, eye, hair, skin, age and future calibrated body constraints.

## Brand Profile and Generation Architecture

Added structured requests for creative, platform, scene, wardrobe, pose, expression, camera, lighting, aspect, routing, count and budget. The prompt builder assembles ten independently versioned layers. A provider protocol and capability/cost/privacy-aware router keep identity above model vendors. The engine attaches the lock, generates candidates, stores metadata, evaluates identity and quality separately, invokes Guardian and queues Founder review.

## Identity Evaluation and Asset Lineage

Evaluation is an extensible port for embedding, feature, experimental and human evidence. Below-70 identity candidates are rejected even with perfect quality. Assets contain reproducibility/disclosure metadata; non-destructive edits link to their parent.

## Founder Feedback, Experiment and Guardian Integration

Structured feedback records Founder reason/category/severity without retraining. `AIRA_VISUAL_IDENTITY_V1` defines eight initial reproducible scenarios for Sprint 017 comparison. Guardian is an injectable port with configurable threshold implementation; Founder decisions remain final.

## Security Review

Reference exposure is restricted through approved provider policy and required capabilities. Documentation mandates least privilege, encryption, hashes, audit, retention/training review, commercial/region approval, controlled provider onboarding and durable tested backups. Provider payload implementations must positively select generation context and exclude unrelated secrets.

## Tests and Test Results

Unit/integration tests cover profile validation, single ACTIVE identity, hierarchy, master immutability, explicit promotion, request validation, ordered prompt layers, routing, generation, independent evaluations, beautiful-but-wrong rejection, Founder override, budget stop, lineage and provider replacement. `pytest` passes (8 tests). Python compile checks pass.

## Known Limitations

This sprint supplies ports and an in-memory reference implementation, not production databases, object storage, UI/Telegram, real provider credentials, embedding/vision models or a generated master binary. Founder-facing surfaces can consume these services but require their own established application adapters. Full-body identity awaits approved calibration. Thresholds require benchmark evidence.

## Technical Debt

Add persistent transactional repositories, RBAC/audit events, encrypted object-store and backup adapters, budget ledgers, production disclosure rules, metrics/report persistence, calibrated multimodal evaluators, dashboard/Telegram endpoints and provider contracts after risk review.

## Recommendations for Sprint 019

Do not start Sprint 019 without Founder approval. First provision the approved reference in protected storage, run restore/hash drills, calibrate `AIRA_VISUAL_IDENTITY_V1` only against approved providers, collect Founder ratings, and select thresholds from multi-scenario evidence rather than a single attractive output.
