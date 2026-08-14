# Contributing to AIRA OS

Changes should be developed on branches and reviewed through pull requests before they reach `main`.

## Integration rules

- Preserve working production paths while integrating historical sprints.
- Do not commit secrets or real user data.
- Prefer one canonical implementation when historical sprints contain duplicate subsystems.
- Keep transport, intelligence, memory, security, and product-domain boundaries explicit.
- Add or update tests when runtime behavior changes.
- Document architecture decisions that materially change subsystem boundaries.

## Historical sprint integration

The `integration/sprints-001-024` branch is used to reconcile early Codex sprint work against the current AIRA OS baseline. Historical pull requests should not be force-merged into `main` when they conflict with newer production code; their useful changes should be adapted and tested first.
