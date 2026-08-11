# Sprint 008 Workflow & Execution Engine Architecture

## Scope

The Workflow & Execution Engine transforms execution plans into controlled workflows. Sprint 008 is architecture-only: it defines models, lifecycle controls, monitoring, incidents, reports, and documentation without real execution, external APIs, message queues, Docker, Kubernetes, browser automation, or external orchestration.

## Lifecycle

```text
Draft -> Validated -> Approved -> Queued -> Running -> Paused -> Waiting Approval -> Resumed -> Completed -> Archived
```

Cancelled is also represented as a terminal safety state for critical failures or founder cancellation.

## Core Objects

### Workflow

A workflow stores an identifier, goal, description, owner, status, priority, stages, dependencies, assigned agents, timestamps, execution history, metrics, incidents, workflow type, execution policy, and approval gates.

### Stage

A stage stores an identifier, title, description, required agent, dependencies, status, input, output, validation rules, retry count, maximum attempts, timeout, and retry policy.

### Execution History

Every controlled action records timestamp, agent, action, result, approval, logs, reason, and sprint version.

### Incident

Every incident records incident ID, workflow ID, cause, impact, resolution, responsible agent, timeline, lessons learned, and creation time.

## Constitution and Guardian Controls

The engine pauses or blocks progress when any Guardian condition fails:

- Constitution violation detected.
- Transparency is missing.
- Evidence is insufficient.
- Required approval is missing.
- Risk is unacceptable.

Founder approval gates are required before publication, brand changes, business decisions, architecture changes, and external actions.

## Monitoring Architecture

The architecture tracks progress, duration, failures, retries, approval delays, incident count, success rate, failure rate, workflow efficiency, and future agent reliability metrics. Monitoring is in-memory for Sprint 008 and can later be connected to durable storage or observability systems.

## Retry and Failure Handling

Recoverable errors use automatic retry when stage policy allows it. Non-recoverable errors pause the workflow, notify the founder through an alert, create an incident, and preserve logs. Critical errors stop the workflow by moving it to cancelled and creating an incident.

## API Surface

The `WorkflowEngine` facade defines architecture methods for:

- Create Workflow
- Update Workflow through state-specific methods
- Pause Workflow
- Resume Workflow
- Cancel Workflow
- Assign Agent
- Track Workflow
- Generate Report
- Archive Workflow
- Search Workflow
- Request Approval
- Handle Failure

## Future Extensions

- Durable workflow repository.
- Message queue backed execution queue.
- Agent availability service.
- Guardian policy service.
- Approval user interface.
- Scheduled workflow triggers.
- Resource usage collector.
- External publishing connectors after founder approval.
