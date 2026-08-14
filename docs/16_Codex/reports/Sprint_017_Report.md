# Sprint 017 Report — Experiment & Tool Testing Engine

## Summary

Implemented the functional experiment-management MVP: versioned protocols, controlled
execution, secure manual result validation, evidence integrity, deterministic metrics,
conservative confidence, nuanced comparison, reporting, approvals, and verified
Knowledge/Experience Memory handoffs. No actual external experiment was performed and
no result in this report is fabricated.

## Experiment Architecture

The stdlib domain layer is independent of executors and orchestration. The in-memory
reference engine enforces lifecycle and emits auditable events. Durable repositories
and infrastructure adapters remain replaceable boundaries.

## Testing Methodology and Experiment Types

Protocols preregister question, hypothesis, inputs, settings, sample size, benchmark,
and approval needs. All specified experiment types are enumerated. Equivalent inputs
and documented environment/settings underpin fair comparisons; tiny samples are
explicitly limited.

## Metrics and Evidence Handling

Metrics preserve raw and normalized values, direction, weights, confidence, evaluator,
and optional rubric. Evidence is an asset reference plus checksum, never a media blob.
Integrity can be rechecked and raw failures cannot be omitted during evaluation.

## Manual Workflow and Mock Executor

Manual entry validates text, numeric metrics, asset references, notes, 0–10 human
ratings, attempt counts, and failure counts. The mock executor deterministically covers
success, failure, timeout, partial, inconclusive, excessive-cost block, and invalid
output scenarios without external effects.

## Knowledge and Memory Integration

Guardian review gates completion. Only completed experiments produce an evidence-linked
Knowledge Candidate; Experience Memory follows it with context, action, outcome,
lesson, confidence, related tool, and related knowledge. Claim verification additionally
requires preserved evidence.

## Security Review and Cost Controls

Declared tool permissions are checked before execution and denial is audited. Paid,
high-risk, or approval-sensitive protocols stop for Founder approval. No purchasing,
credential creation, browser automation, publishing, or untrusted execution exists.

## Tests and Test Results

The Sprint suite covers creation, validation, metric normalization, evidence linking
and tampering, protocol history, costs, risk approval, manual input, all mock outcomes,
comparison, conservative confidence, lifecycle transitions, permission denial,
Guardian/Knowledge/Memory flow, claim boundaries, and regression history. Exact run
results are recorded in the commit/PR validation output rather than invented here.

## Known Limitations and Technical Debt

- Persistence and asset authorization are adapter work; storage is currently in-memory.
- Guardian, Knowledge, Memory, Research, and event-bus integrations are stable handoff
  contracts/callbacks rather than deployed service clients.
- Regression detection is event-capable but benchmark selection and scheduling remain
  orchestration work.
- The confidence formula is deliberately simple and requires calibration on genuine
  experiment history.
- Real API/browser/media/CLI executors are out of scope and intentionally absent.

## Recommendations for Sprint 018

Do not begin Sprint 018 without Founder approval. When approved, prioritize durable
repositories, asset-store authorization, transactional event delivery, and integration
contract tests while retaining raw-evidence immutability and human approval boundaries.
