# Experiment & Tool Testing Engine

Sprint 017 provides an evidence-first, side-effect-free experiment-management
workflow. The reference implementation lives in `backend/experiments` and uses an
in-memory repository so its policy and domain layer can be integrated with durable
storage later.

## Workflow

1. Build an `Experiment`, `Protocol`, environment, test cases, and metrics.
2. Call `create_experiment`; high-risk, paid, or explicitly sensitive protocols wait
   for Founder approval.
3. Approve if required, then use `MockTestExecutor`, or securely enter a manual
   `TestResult`. Every requested tool must be present in `tool_permissions`.
4. Reference raw files through asset-storage URIs and record a SHA-256 checksum.
   Relational objects never contain large media blobs.
5. Evaluate only after every test case—including every failure—is recorded.
6. Guardian reviews the method, claim, limitations, and confidence. It cannot edit
   evidence through this API.
7. Only a verified `COMPLETED` experiment can create a Knowledge Candidate; Memory
   handoff follows Knowledge handoff. Content systems consume the resulting
   knowledge, not unfinished raw results.

The claim guard `has_verified_test_claim(tool)` is true only for a Guardian-verified
experiment with evidence. Therefore AIRA cannot truthfully say “I tested this” from
research, a proposed protocol, or an evidence-free record.

## Public API

`ExperimentEngine` exposes creation, protocol updates, approval, execution, manual
result entry, evidence linking and integrity verification, deterministic evaluation,
Guardian review, comparison, reporting, search, Knowledge/Memory handoff, and claim
verification. Events are retained in an audit list and may also be delivered to an
injected event sink.

See the focused architecture and policy documents in this directory for design
details. No browser automation, purchases, external-account creation, real provider
execution, publishing, or public recommendations are implemented.
