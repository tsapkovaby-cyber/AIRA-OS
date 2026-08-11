# Sprint 018 Report — Visual Identity & Digital Human Engine

## Summary

Sprint 018 implements the domain and policy foundation for reproducing one canonical AIRA across provider-independent image workflows. It does not redesign AIRA, generate a replacement face, or begin Sprint 019.

## Canonical Identity

`AIRA_VISUAL_IDENTITY_PACK_V1` is ACTIVE and Founder-approved. Its reference-backed profiles encode the approved young-adult presentation, natural feminine face, light skin, long light-blonde hair, critical blue eyes, and natural makeup. The reference remains authoritative over text attributes.

## Master Reference Registration

`AIRA_MASTER_REFERENCE_V1` is registered using the Asset Management URI `asset://canonical/aira/master/v1`, marked Founder-approved and read-only. The repository intentionally contains metadata, not the sensitive image binary. Production Asset Storage owns the verified content checksum and backup replicas.

## Identity Profile

The implementation includes identity/character/version/status, approval, master and reference set, face/hair/eye/skin/body/makeup/brand profiles, wardrobe and variation rules, timestamps, and history. Registry policy permits only one ACTIVE identity for a character.

## Reference Hierarchy

Four ordered levels distinguish master, Founder-approved, test, and generated assets. Canonical references require Founder approval. Generated content cannot implicitly enter the reference set.

## Identity Lock

The lock requires canonical references and separates stable face, eye, hair, skin, age, body, and identity-strength constraints from variable scene styling.

## Brand Profile

The profile captures clean photorealism, the controlled neutral/violet/burgundy palette, recurring white-shirt signature, and anti-cyberpunk realism direction. Wardrobe, scene, lighting, and camera may vary without redefining identity.

## Generation Architecture

Typed requests validate platform aspect ratio, candidates, references, and request cost. Prompt assembly has ten ordered, independently versionable layers. Important generations default to multiple candidates and Founder review.

## Visual Provider Layer

The provider protocol covers generation, editing, variations, capabilities, cost, and health. Capability routing considers only healthy Founder-approved providers and blocks over-budget work for approval. Provider profiles capture privacy and commercial-use governance.

## Identity Evaluation

Pluggable identity and quality evaluators remain distinct. Identity failure rejects even a high-quality image; Guardian review follows both thresholds. This contract supports future embeddings, visual evaluators, experiment data, and manual review rather than relying on one LLM opinion.

## Asset Lineage

Typed assets retain all generation inputs, storage pointer/checksum, parent, status, scores, rights, and disclosure state. Parent validation and new child assets enforce non-destructive editing.

## Founder Feedback

Founder decisions override automation. Rejections become structured feedback with target, category, severity, reason, decision, and timestamp. Feedback is memory for prompting/experiments, not permission for uncontrolled training.

## Experiment Integration

`AIRA_VISUAL_IDENTITY_V1` defines eight initial controlled benchmark scenarios. Provider implementations can use the shared request, routing, evaluator, latency/cost, and approval records to produce consistency reports for Sprint 017 experiments.

## Security Review

Master overwrite and automatic promotion are denied. Provider routing requires prior Founder approval, and the request contract contains no unrelated Founder-private context. Binaries remain outside ordinary database objects. Operational deployment must implement least-privilege downloads, audit logs, verified checksums, encrypted replicated backups, and provider-specific retention enforcement.

## Tests

Tests cover profile and hierarchy validation, ACTIVE uniqueness, master protection, request validation, layered prompts, lineage, Founder-only promotion, routing, budgets, feedback, beautiful-but-wrong rejection, drift rejection, Founder override, and privacy-minimized requests.

## Test Results

The Sprint 018 test suite passes locally under Python 3.11+ using `pytest`.

## Known Limitations

- No Founder image binary was committed; Asset Storage must resolve the registered URI and replace the checksum placeholder with its verified digest during secure deployment.
- Evaluator interfaces are implemented, but production face embeddings and visual-quality models require approved provider adapters and calibration data.
- Persistence is in-memory at this domain-foundation stage; a transactional repository must enforce ACTIVE uniqueness and immutable master records in production.
- Dashboard, Telegram previews, and publication adapters are not present in this initial repository and therefore expose no Sprint 018 UI yet.
- Full-body identity remains deliberately uncalibrated pending Founder-approved references.

## Technical Debt

- Add persistent repositories, migrations, audit identities, retention jobs, and backup recovery drills.
- Add provider adapters only after risk and experiment approval.
- Calibrate thresholds and composite scoring against Founder benchmark ratings.
- Connect Guardian, Experiment, Content, Publishing, Dashboard, and Telegram applications as those subsystems enter this repository.

## Recommendations for Sprint 019

Do not start Sprint 019 without Founder approval. Before future modality work, securely ingest and verify the supplied master binary, run the eight-scenario benchmark against approved providers, collect Founder calibration feedback, approve additional angle/full-body references, and validate restore procedures.
