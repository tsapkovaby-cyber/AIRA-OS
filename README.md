# AIRA-OS

AIRA OS is the repository for AIRA, a virtual AI assistant and digital-human platform.

## Current baseline

The current production baseline contains the Telegram MVP, privacy-policy hosting, deployment configuration, and the OpenAI SDK compatibility fix used by the Railway deployment.

## Historical sprint integration

Early Codex sprints were developed in parallel branches and are being reconciled on `integration/sprints-001-024` before any consolidated merge into `main`.

Integration priorities are:

1. preserve the working Telegram/deployment baseline;
2. consolidate repository and core architecture;
3. integrate Memory, Knowledge, Research, Decision, Planner, Workflow, Guardian, Content, Publishing, Agents, Intelligence and Retrieval;
4. select one canonical Digital Human implementation where historical work overlaps;
5. integrate Perception, Telegram gateway, AIRA Academy and the Live Language Classroom;
6. run regression tests before promoting the integrated system to `main`.

## Integrated foundations

- Sprint 002: provider-agnostic AIRA Core contracts for Identity, Decision, Memory, Knowledge, Research, Content, Guardian, and Growth under `backend/core/`.
- Sprint 003: concrete reference Memory Engine under `aira_memory/` with JSON persistence, append-only versions, relationship mapping, permission checks, audit events, lifecycle operations, and structured search. It is retained behind the Sprint 002 Memory abstraction for later adapter integration rather than being wired directly into the live Telegram runtime.
- Sprint 004: provider-independent Knowledge Graph architecture under `docs/architecture/knowledge-graph/`, with canonical JSON schemas and examples for connected, versioned, traceable and explainable knowledge. The graph is treated as a knowledge-domain layer above Memory rather than a replacement persistence system.
- Sprint 005: Research Engine under `src/aira_os/research_engine/` that validates, normalizes, scores, deduplicates and records conflicts in research items, and stops at a `KnowledgeCandidate` handoff. Research is not allowed to publish or become authoritative knowledge by itself.
- Sprint 006: Decision Engine under `src/aira_os/decision_engine/` for evidence-first, explainable decisions with confidence/risk classification and explicit Founder approval. During integration, approval and rejection were hardened so non-Founder actors cannot approve sensitive decisions.
- Sprint 007: Planner Engine under `src/aira_os/planner_engine/` converts goals into dependency-checked execution plans without executing them. Founder-only plan approval/rejection is enforced before tasks can move to the queued state.

## Architecture references

- [Knowledge Graph Engine](docs/architecture/knowledge-graph/README.md)
- [Sprint S004 Architecture Report](docs/sprints/S004/architecture-report.md)
- [Research Engine Architecture](docs/research_engine/ARCHITECTURE.md)
- [Research Engine Workflow](docs/research_engine/WORKFLOW.md)
- [Decision Engine Architecture](docs/decision_engine/ARCHITECTURE.md)
- [Planner Engine](docs/sprints/S007_PLANNER_ENGINE.md)

Secrets and private user data must never be committed to this repository. See `SECURITY.md`.
