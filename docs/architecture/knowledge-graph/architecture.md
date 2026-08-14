# Knowledge Graph Engine Architecture

## Architectural Position

The Knowledge Graph Engine is an architectural subsystem responsible for defining how AIRA records, relates, versions, searches, and explains knowledge. It is intentionally provider independent: the same contracts can be backed by files, SQL, graph databases, document stores, memory services, or future AI-native stores.

## Core Principles

| Principle | Architectural Meaning |
| --- | --- |
| Connected | Nodes are valuable because of relationships, not only because of their attributes. |
| Versioned | Every material change creates a recoverable historical version. |
| Traceable | Knowledge must identify references, evidence, ownership, and provenance. |
| Explainable | Recommendations and paths must expose why a conclusion was reached. |
| Expandable | New node types, relationship types, scores, and providers can be added without changing the core model. |
| Provider Independent | Interfaces define capabilities; adapters provide persistence and search behavior later. |

## Conceptual Components

```text
Client / Future Services
        |
        v
Graph API Contracts
        |
        v
Graph Operation Interfaces
        |-------------------------------|
        v                               v
Graph Model Contracts             Explainability Contracts
        |                               |
        v                               v
Provider Adapter Boundary      Evidence / Path Model
        |
        v
Future Persistence Providers
```

## Component Responsibilities

### Graph API Contracts

Defines operations such as node creation, relationship creation, graph search, shortest path, subgraph export, and explain graph. These contracts do not prescribe storage technology.

### Graph Model Contracts

Defines the canonical node, relationship, layer, score, evidence, conflict, and version fields.

### Graph Operation Interfaces

Defines operation intent and validation boundaries for create, update, archive, merge suggestion, split suggestion, traversal, orphan detection, and relationship suggestion.

### Explainability Contracts

Defines how an answer links back to paths, evidence, references, confidence, and historical versions.

### Provider Adapter Boundary

Defines where a future file, SQL, graph database, or service-backed adapter can be attached. Sprint S004 does not implement adapters.

## Graph Layers

| Layer | Name | Purpose |
| --- | --- | --- |
| 1 | Identity Graph | Defines who AIRA is, including constitution, identity, values, operating constraints, and approved self-description. |
| 2 | Knowledge Graph | Stores facts, definitions, concepts, frameworks, platforms, APIs, tools, papers, and models. |
| 3 | Experience Graph | Stores experiments, lessons learned, test outcomes, failures, observations, and practical evidence. |
| 4 | Project Graph | Stores repositories, roadmap items, sprints, RFCs, architecture decisions, issues, tasks, and releases. |
| 5 | User Graph | Stores user preferences, goals, interactions, and approved memory. |
| 6 | Content Graph | Stores articles, videos, posts, scripts, templates, media, and performance context. |

## Data Lifecycle

1. A proposed node or relationship is submitted through a graph contract.
2. The proposal is validated against schema, allowed types, visibility, ownership, confidence, and required evidence rules.
3. The graph records the accepted version as current.
4. Prior versions remain accessible as historical knowledge.
5. Search and traversal interfaces expose current and historical views.
6. Explainability output cites evidence, versions, path segments, and confidence.

## Versioning Model

Knowledge never disappears. Archive operations change active visibility without deleting historical versions. Updates create new versions and preserve previous values. Merge and split operations are approval-gated proposals, not automatic destructive operations.

## Conflict Model

Conflicting claims are stored as separate nodes, relationship evidence, or versioned assertions. The graph compares confidence and evidence but does not hide disagreement. Consumers must be able to inspect conflicting sources and reasoning.

## Duplicate Model

Duplicate concepts are detected as candidates by title similarity, tag overlap, reference overlap, and relationship overlap. Merge is never automatic. A human-approved merge creates a new versioned state and preserves the pre-merge nodes as historical references.

## Scoring Model

Every node can carry these independent scoring dimensions:

- Confidence
- Importance
- Freshness
- Popularity
- Business Value
- Educational Value
- Completeness

Scores are advisory metadata. The architecture does not implement ranking business logic in S004.
