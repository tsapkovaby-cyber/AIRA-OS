# Architecture

The engine separates immutable-style domain records (`models.py`), executor contracts
(`executors.py`), and lifecycle/policy orchestration (`engine.py`). `TestExecutor` is
an extension point; Sprint 017 deliberately ships only deterministic
`MockTestExecutor`. Manual input uses the same normalized `TestResult` schema.

Lifecycle transitions are explicit. Protocol edits increment both experiment and
protocol versions and are rejected after execution begins. History snapshots preserve
the earlier hypothesis. Terminal failures remain stored. Approval checks occur before
execution, while Guardian verification gates Knowledge handoff.

Adapters for a database, asset store, event bus, Guardian, Knowledge Engine, and
Memory Engine are integration work: current handoffs are typed dictionaries with
stable experiment/version references and an optional event callback.
