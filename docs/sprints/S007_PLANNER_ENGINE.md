# Sprint 007 — Planner Engine Architecture Report

## Purpose

The Planner Engine converts high-level goals into structured execution plans. It never executes work itself; it coordinates execution by producing approval-gated task graphs for specialized agents.

## Scope

Included:

- Goal model
- Task model
- Workflow model
- Dependency validation and ordering
- Agent assignment metadata
- Approval workflow
- Progress reports
- Roadmap update hooks
- Unit-testable architecture

Excluded:

- Execution logic
- Scheduling service
- Background workers
- Calendar integration
- Notifications

## Architecture

`aira_os.planner_engine` is split into three layers:

1. `models.py` defines immutable and mutable planning artifacts.
2. `dependencies.py` validates missing, duplicate, and circular dependencies, then produces dependency-safe ordering.
3. `engine.py` exposes the Planner API and stores in-memory plan state for architecture-level use.

## Planning Pipeline

1. Receive goal.
2. Understand objective.
3. Determine scope via goal type and planning level.
4. Select workflow template.
5. Generate tasks.
6. Validate dependencies.
7. Prioritize tasks.
8. Assign agents by phase.
9. Request Guardian/founder approval.
10. Queue approved tasks for external execution systems.
11. Monitor progress from task statuses.
12. Record retrospective information through plan history and roadmap updates.

## Task Model

Each task includes:

- Task ID
- Title and description
- Priority
- Status
- Owner
- Agent
- Dependencies
- Estimated duration, difficulty, risk, confidence, and resource usage
- Business value
- Deadline
- Created and updated timestamps
- History

## Workflow Templates

Initial templates cover:

- Telegram Post
- Research
- Development Architecture
- Campaign
- Generic Planning

Templates describe phase order and execution strategy only. They do not execute the phases.

## API

The Planner Engine exposes:

- `create_goal`
- `generate_plan`
- `update_plan`
- `request_approval`
- `approve_plan`
- `reject_plan`
- `archive_plan`
- `assign_agent`
- `search_plans`
- `track_progress`
- `generate_report`

## Dependency Management

The dependency engine detects:

- Missing dependencies
- Circular dependencies
- Duplicate task titles
- Self-dependencies at model construction

It also produces a topological task order for valid task graphs.

## Planner Memory

Every plan contains task history, approval transitions, dependency findings, and roadmap update notes. These records form the basis for future retrospective and planning-accuracy improvements.

## Future Extensions

- Persistent plan repository
- Rich scoring for workload and risk
- Calendar and task-queue adapters after founder approval
- Retrospective metrics store
- Cross-plan dependency analysis
- Agent capacity forecasting
