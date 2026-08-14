# Knowledge Graph Model

## Node Categories

The architecture supports these initial node categories:

- AI Model
- AI Tool
- Company
- Person
- Research Paper
- Prompt
- Workflow
- Automation
- Content
- Conversation
- Decision
- Experiment
- Project
- Task
- Business
- Platform
- API
- Framework
- Programming Language
- Database
- Agent
- Memory
- Document
- Idea
- Feature
- Release
- Issue
- RFC
- Roadmap Item

New categories may be added through versioned schema evolution.

## Relationship Types

The architecture supports these initial relationship types:

- USES
- CREATED_BY
- BELONGS_TO
- RELATED_TO
- SIMILAR_TO
- ALTERNATIVE_TO
- REPLACES
- GENERATES
- TESTED_IN
- MENTIONED_IN
- DOCUMENTED_IN
- LEADS_TO
- DEPENDS_ON
- IMPROVES
- INSPIRED_BY
- SUPERSEDES
- CONNECTS_TO
- PART_OF
- REQUIRES
- APPROVED_BY
- OWNED_BY

## Node Structure

| Field | Required | Description |
| --- | --- | --- |
| id | Yes | Unique stable node identifier. |
| title | Yes | Human-readable concept title. |
| description | Yes | Clear explanation of the concept. |
| category | Yes | Node category from the controlled category list. |
| layer | Yes | Graph layer number from 1 to 6. |
| tags | Yes | Searchable labels. |
| createdDate | Yes | ISO 8601 creation timestamp. |
| updatedDate | Yes | ISO 8601 update timestamp. |
| version | Yes | Semantic or monotonically increasing version string. |
| confidence | Yes | Confidence score from 0 to 1. |
| visibility | Yes | Visibility state: public, internal, private, restricted, archived. |
| owner | Yes | Responsible person, agent, system, or organization. |
| references | Yes | Source references and provenance. |
| relatedNodes | Yes | Related node identifiers or relationship identifiers. |
| scores | Yes | Node scoring dimensions. |
| historicalVersions | Optional | References to retained historical versions. |

## Relationship Structure

| Field | Required | Description |
| --- | --- | --- |
| id | Yes | Unique stable relationship identifier. |
| sourceNodeId | Yes | Source node identifier. |
| targetNodeId | Yes | Target node identifier. |
| type | Yes | Relationship type from the controlled type list. |
| strength | Yes | Relationship strength from 0 to 1. |
| reason | Yes | Human-readable explanation of why the relationship exists. |
| evidence | Yes | Evidence records supporting the relationship. |
| createdDate | Yes | ISO 8601 creation timestamp. |
| version | Yes | Relationship version. |
| confidence | Yes | Confidence score from 0 to 1. |
| visibility | Yes | Visibility state. |

## Evidence Structure

Evidence records preserve traceability and explainability.

| Field | Required | Description |
| --- | --- | --- |
| id | Yes | Unique evidence identifier. |
| sourceType | Yes | document, url, conversation, experiment, observation, repository, or manual. |
| citation | Yes | Human-readable citation or source pointer. |
| summary | Yes | Concise statement of what the evidence supports. |
| confidence | Yes | Evidence confidence from 0 to 1. |
| observedDate | Optional | Date the evidence was observed. |

## Explainable Path Structure

An explainable path contains ordered path segments:

1. Recommendation or requested conclusion.
2. Supporting knowledge node.
3. Supporting experience node.
4. Supporting experiment or source node.
5. Evidence references.
6. Confidence and caveats.

## Historical Knowledge Rules

- Updates do not overwrite history.
- Archive operations retain old versions.
- Conflict records remain inspectable.
- Merge proposals preserve original node identifiers in historical references.
- Split proposals record the parent node and generated child nodes.
