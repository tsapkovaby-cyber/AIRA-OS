# Knowledge Graph Examples

## Example Node

See [`examples/knowledge_graph/node.example.json`](../../../examples/knowledge_graph/node.example.json).

## Example Relationship

See [`examples/knowledge_graph/relationship.example.json`](../../../examples/knowledge_graph/relationship.example.json).

## Example Explainability Flow

Recommendation: Use a workflow for an API integration.

1. Workflow node is connected to an API node through `USES`.
2. API node is connected to documentation through `DOCUMENTED_IN`.
3. Experiment node is connected to workflow through `TESTED_IN`.
4. Evidence records cite the documentation and experiment summary.
5. Confidence is calculated later by a provider or service, but the architecture requires the value to be present and explainable.

## Example Conflict

If one research paper says Tool A improves a workflow and another says Tool A degrades that workflow, the graph stores both relationships or claims with separate evidence. Consumers compare confidence, date, scope, and evidence rather than deleting the weaker claim.

## Example Duplicate Candidate

Two nodes named "Prompt Optimization" and "Prompt Tuning" may be suggested as merge candidates when they share tags, references, and relationships. The system must not merge them without human approval.
