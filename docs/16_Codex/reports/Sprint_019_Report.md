# Sprint 019 Report — Voice Identity & Speech Engine

**Sprint:** S019 · **Version:** 1.0 · **Result:** Implemented · **Date:** 2026-08-10

## Summary

Sprint 019 establishes a provider-independent, Founder-derived AIRA voice domain.
It does not synthesize production speech or upload the reference. It provides the
policy-bearing models, abstractions, selection pipeline, evaluation, tests and
permanent canon needed to do so safely once real provider experiments are approved.

## Master Voice Registration

`AIRA_MASTER_VOICE_REFERENCE_V1` is registered as read-only, active and
Founder-approved, belonging to `AIRA_VOICE_IDENTITY_V1`. Its secure URI and pending
ingest hash are metadata only because no source audio binary was available in the
repository. The code prevents ordinary master replacement and models separately
hashed child derivatives. Secure binary ingest remains an operational Founder task.

## Voice Identity Architecture

Immutable domain models cover identity lifecycle, references, the identity lock,
requests, provider profiles, speech assets, feedback and budgets. Identity and
style are separate. The lock treats pace/emotion as allowed variation and speaker,
timbre, material pitch and identity as forbidden variation.

## Consent Model

Consent records Founder provenance, AIRA-only scope, disabled automatic sharing
and mandatory provider policy review. Profile construction fails if character and
consent disagree. Generated assets disclose AIRA as speaker, Founder-derived voice
source and generated status.

## Voice Canon

The permanent canon records voice philosophy, custody, hierarchy, language,
pronunciation, scoring and Founder authority in
`docs/02_AIRA_Identity/AIRA_VOICE_CANON.md`.

## Speech Profiles

Telegram, short video, long video, education, intro and experiment task names are
documented. Controlled emotions and paces are typed. High-risk requests cannot be
constructed without Founder approval.

## Pronunciation System

The Russian/English seed lexicon contains all requested AI and platform terms.
AIRA's brand pronunciation is explicitly pending Founder review rather than guessed.

## Provider Layer and Voice Router

The abstract adapter supports synthesis, capability discovery, estimation, health,
reference/clone/emotion support and future streaming. The router admits only
healthy, approved, language-compatible providers and sorts identity similarity
before quality and cost. An approved external profile—not the master file—is passed
to adapters.

## Voice Evaluation and Founder Feedback

Evaluation keeps identity and quality independent. Identity below 70 rejects,
70–79 requests Founder review, and 80+ proceeds to quality evaluation. Founder
rejection overrides even a 94 score and is retained as structured feedback.

## Security and Guardian

Guardian compares provider output with approved text exactly; silent text changes
fail. The domain disallows missing lineage and false Founder/authentic-recording
metadata. Provider status gates prevent blind upload architecture. High-risk and
impersonation restrictions are documented.

## Cost Controls

Per-request, daily, monthly and experiment caps are implemented. The engine returns
`WAITING_FOUNDER_APPROVAL` before synthesis when a request exceeds request or
aggregate limits. Asset metadata supports later characters, seconds, rejected
generation and cost-per-approved-minute aggregation.

## Experiment Integration

`AIRA_VOICE_BENCHMARK_V1` defines ten standardized scenarios, eleven comparison
metrics and mandatory Founder evaluation. It is a local Experiment Engine contract;
persisted experiment execution awaits a concrete Sprint 017 service in this
minimal repository.

## Digital Human Integration

`DigitalHumanProfile` now binds the canonical visual identity ID,
`VoiceIdentityProfile`, behavior profile and AIRA core identity while preventing a
non-AIRA voice attachment. Together the intended IDs are
`AIRA_VISUAL_IDENTITY_V1`, `AIRA_VOICE_IDENTITY_V1` and
`AIRA_DIGITAL_HUMAN_V1`; the prior visual implementation was not present here.

## Tests and Test Results

Automated tests cover profile/consent validation, master protection, reference
hierarchy, request and pronunciation rules, high-risk review, routing denial and
identity priority, lineage, budgets, exact text integrity, drift rejection,
beautiful-but-wrong rejection and Founder override.

`python -m pytest -q`: **6 passed in 0.11s**.

## Known Limitations

- The source audio binary was not in the checkout, so secure ingest, real analysis
  and the final SHA-256 cannot truthfully be completed.
- There is no external provider adapter, upload, production storage or real audio
  quality/voice embedding scorer; this intentionally avoids arbitrary disclosure.
- Identity thresholds are conceptual and require controlled Founder calibration.
- Streaming, speech-to-speech, phone calls, lip sync, motion and video are out of scope.

## Technical Debt

- Add a durable repository enforcing a database-level single-active-profile rule.
- Implement access-controlled object storage, immutable retention and audit events.
- Add a real audio analyzer and semantic transcript verification after approval.
- Connect cost usage, Guardian and Experiment Engine to persistent core services
  when those earlier-sprint modules are made available in this repository.

## Recommendations for Sprint 020

Do not begin Sprint 020 without Founder approval. First securely ingest and hash the
recording, approve AIRA pronunciation samples, calibrate identity scoring, research
candidate provider policies, and authorize only bounded benchmark uploads. Preserve
the original and retain every experiment's evidence, consent, cost and lineage.
