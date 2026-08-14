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

## Sprint 003: Memory Engine

Sprint 003 contributes a provider-neutral reference Memory Engine in `aira_memory/` with JSON persistence, append-only versions, relationships, permissions, audit events, lifecycle operations, and structured search. It is being retained as the persistence/reference implementation behind the architecture-first Memory contract introduced by Sprint 002; later integration work can add an adapter between the two without changing the production Telegram runtime.

See `docs/memory-engine-architecture.md` for the Sprint 003 architecture report.

Secrets and private user data must never be committed to this repository. See `SECURITY.md`.
