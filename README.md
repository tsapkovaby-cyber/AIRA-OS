# AIRA-OS

AIRA-OS is the architecture repository for AIRA operating system sprints.

## Sprint 008 — Workflow & Execution Engine

Sprint 008 adds an architecture-only Workflow & Execution Engine. The engine transforms execution plans into controlled workflows, coordinates stage assignment, records execution history, monitors progress, handles retry and incident policy, and enforces Founder and Guardian oversight before sensitive actions.

### What is included

- Workflow, stage, execution history, incident, metric, retry, approval gate, lifecycle, workflow type, and execution policy models.
- In-memory workflow engine facade for architecture validation.
- Canonical workflow templates for Telegram posts, AI tool reviews, and new AI news.
- Architecture documentation and an executable example.
- Unit tests for creation, validation, dependencies, retry logic, approval gates, history, incidents, and monitoring.

### What is intentionally excluded

Sprint 008 does not implement real execution, message queues, Kubernetes, Docker orchestration, external APIs, or browser automation.

### Quick start

```bash
python -m pytest
python examples/telegram_post_workflow.py
```

### Documentation

See [`docs/workflow_engine_architecture.md`](docs/workflow_engine_architecture.md) for the architecture report, API surface, monitoring design, Guardian integration, failure handling, and future extensions.
