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

Secrets and private user data must never be committed to this repository. See `SECURITY.md`.
