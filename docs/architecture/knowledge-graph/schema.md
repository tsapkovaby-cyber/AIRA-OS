# Knowledge Graph Schema

The canonical architecture schemas are stored as JSON Schema files:

- [`schemas/knowledge_graph/node.schema.json`](../../../schemas/knowledge_graph/node.schema.json)
- [`schemas/knowledge_graph/relationship.schema.json`](../../../schemas/knowledge_graph/relationship.schema.json)

## Schema Evolution

Schema changes must be versioned. Additive changes are preferred. Breaking changes require migration guidance, historical compatibility notes, and Founder approval.

## Validation Expectations

A valid node must include identity, category, layer, tags, timestamps, version, confidence, visibility, owner, references, related node pointers, and scores.

A valid relationship must include source, target, type, strength, reason, evidence, timestamp, version, confidence, and visibility.
