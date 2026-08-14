# Guardian Architecture Report

## Purpose

Guardian is an independent control layer for AIRA workflows. Its purpose is to protect trust, protect users, protect knowledge quality, and ensure every public action is transparent, explainable, and verifiable.

## Design Boundaries

Guardian is intentionally architecture-only in Sprint 009:

- no AI moderation implementation;
- no legal automation;
- no external compliance integrations;
- no automatic censorship;
- no production database dependency.

The current implementation uses deterministic policy helpers and in-memory stores so future sprints can replace storage, workflow execution, and notification adapters without changing the policy vocabulary.

## Components

### Models

`guardian_engine.models` defines the canonical review object, evidence object, incident object, risk categories, risk levels, review results, approval status, and claim-type labels.

### Policies

`guardian_engine.policies` defines architecture rules for evidence requirements, Founder approval domains, Constitution checklist coverage, and risk classification.

### Engine

`guardian_engine.engine.GuardianEngine` orchestrates the validation pipeline, stores review and incident history, generates reports, and exposes the Guardian API.

## Authority

Guardian has the authority to return `Blocked`, `Rejected`, `Escalated`, or `Needs Revision`. A blocked review creates an incident, sets Founder notification as required, and stores suggested resolution guidance.

## Memory Architecture

Sprint 009 stores reviews, incidents, and transparency logs in memory. Future persistence adapters should store:

- reviews;
- incidents;
- corrections;
- lessons learned;
- false positives;
- policy updates.

## Metrics Architecture

Future metrics can be computed from review and incident records:

- approval rate;
- rejection rate;
- revision rate;
- average review time;
- false-positive rate;
- critical incidents;
- Constitution violations.
