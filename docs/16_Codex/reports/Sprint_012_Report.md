# Sprint 012 Report — Agent Framework & Agent Registry

## Summary

Sprint 012 establishes a safe, modular agent control plane. Agents remain specialized workers beneath AIRA Core. Execution is registered, Workflow-assigned, scoped, Guardian-aware, auditable, and globally pausable.

## Agent Registry Structure

The domain defines manifests, lifecycle/health states, structured tasks/results, model settings, budgets, tools, and audit records. `AgentRegistry` validates identity, versions, approved prompts, registered tools, agent-type allowlists, and permission prerequisites. It exposes lookup/listing, metadata, lifecycle, health, version history, tools, and startup validation. Candidate versions remain inactive pending controlled rollout.

## Agent Profiles Added

The catalog documents Research, Knowledge, Memory, Content, Guardian, Analytics, Business, Publishing, and CEO Assistant without introducing roles or increasing specified autonomy.

## Permissions Added

Typed least-privilege permissions cover research, knowledge, memory, drafts, analytics, approved publication, LLM/web/voice, workflow blocks, and planning requests. Task-bound temporary permission grants require a distinct authorized approver and support expiry.

## Tool Policies

Tools register independently with risk, allowed types, required permissions, limits, and audit policy. Both manifest and task must allow a tool. Unknown or incompatible tools fail closed; no universal tool or credential delivery exists.

## Memory Policies

Eight explicit memory scopes are modeled. `NONE` is exclusive and unauthorized scope requests fail. Context is reduced to task-relevant data and marks external content as data.

## Prompt Registry

Immutable prompt versions use content references and approval state. Resolution selects an explicit or latest approved version. Registration/startup fail on missing prompt references.

## Provider Abstraction

`ModelProvider` and `ProviderRegistry` decouple execution from vendors. Per-agent non-secret configuration captures model, temperature, output/timeout/tool/schema limits and fallback reference. Real adapters and credentials remain out of scope.

## Tests

Unit/integration coverage includes registration, duplicates, schema validation, tool/permission/memory authorization, lifecycle/health, temporary expiry/self-grant prevention, global pause, prompt versions, unknown-agent and Workflow bypass rejection, structured output/audit flow, and Guardian blocking.

## Test Results

`pytest` passes all Sprint 012 tests. The repository-wide suite is currently the Sprint 012 Python suite because this repository began with only its README.

## Security Findings

Fail-closed boundaries are in place. Execution cannot begin for unknown/unready agents, outside Workflow, during global pause, after Guardian denial, or with undeclared tools. Audit entries expose lifecycle and execution. No secrets, production network, publishing, shell, direct agent messaging, or self-modification were added.

## Known Limitations

Storage is in-memory; rate/cost budgets are modeled but enforcement persistence and distributed counters are future work. Provider fallback is configuration-only. Cancellation is cooperative at the runtime boundary. Concrete Planner, Event Bus, incident service, memory adapters, and production sandbox integration await later approved sprints.

## Technical Debt

Add durable transactional repositories, cryptographic/tamper-evident audit storage, schema payload validation, concurrency leases, distributed circuit-breaker state, rate/cost meters, incident emission, and provider conformance tests once their infrastructure exists.

## Recommendations for Sprint 013

Do not begin without Founder approval. Next work should integrate these stable contracts through adapters rather than weakening registry/runtime boundaries, and should prioritize durable audit and explicit incident integration.
