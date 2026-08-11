# Knowledge Graph API Contracts

## API Style

Sprint S004 defines provider-independent contracts, not a runtime API implementation. Future implementations may expose these contracts through REST, GraphQL, RPC, local SDKs, or internal service interfaces.

## Graph Operations

| Operation | Intent | Destructive |
| --- | --- | --- |
| createNode | Create a validated node. | No |
| updateNode | Create a new current version of an existing node. | No |
| archiveNode | Mark a node archived while retaining history. | No |
| mergeNodes | Submit or apply an approved merge proposal. | Approval-gated |
| splitNode | Submit or apply an approved split proposal. | Approval-gated |
| createRelationship | Create a validated relationship. | No |
| removeRelationship | Archive or deactivate a relationship while retaining history. | No |
| searchGraph | Search nodes and relationships. | No |
| explainPath | Explain why nodes or conclusions are connected. | No |
| generateSubgraph | Return a bounded subgraph around selected nodes. | No |
| findSimilarNodes | Return duplicate or similarity candidates. | No |
| detectOrphans | Find nodes without meaningful relationships. | No |
| suggestRelationships | Return relationship candidates for human review. | No |

## Search Capabilities

| Capability | Contract Definition |
| --- | --- |
| Keyword Search | Match text against title, description, tags, references, and evidence summaries. |
| Semantic Search | Interface placeholder for future provider-backed meaning search. Not implemented in S004. |
| Graph Traversal | Traverse relationships by depth, type, layer, direction, confidence, and visibility. |
| Relationship Search | Filter relationships by type, source, target, evidence, strength, or confidence. |
| Shortest Path | Return the shortest valid relationship path between two nodes under constraints. |
| Tag Search | Filter nodes by one or more tags. |
| Category Search | Filter nodes by category and layer. |
| Time Search | Filter nodes and relationships by created, updated, observed, or version dates. |
| Confidence Search | Filter nodes, relationships, and evidence by confidence ranges. |

## Contract Examples

### createNode

Input:

```json
{
  "title": "Example API",
  "description": "A documented API concept.",
  "category": "API",
  "layer": 2,
  "tags": ["api", "example"],
  "owner": "AIRA",
  "visibility": "internal",
  "confidence": 0.8,
  "references": []
}
```

Output:

```json
{
  "nodeId": "node_api_example",
  "version": "1.0.0",
  "status": "created"
}
```

### createRelationship

Input:

```json
{
  "sourceNodeId": "node_workflow_example",
  "targetNodeId": "node_api_example",
  "type": "USES",
  "strength": 0.75,
  "reason": "The workflow calls the API to complete its task.",
  "evidence": []
}
```

Output:

```json
{
  "relationshipId": "rel_workflow_uses_api",
  "version": "1.0.0",
  "status": "created"
}
```

## Explain Graph Response Shape

```json
{
  "question": "Why is this workflow recommended?",
  "conclusion": "The workflow is related to the selected project because it uses the same API and improves an approved task.",
  "paths": [
    {
      "segments": [
        { "from": "node_workflow", "relationship": "USES", "to": "node_api" },
        { "from": "node_task", "relationship": "REQUIRES", "to": "node_api" }
      ],
      "evidence": ["evidence_api_docs"],
      "confidence": 0.78
    }
  ],
  "conflicts": [],
  "caveats": ["Semantic ranking is not implemented in Sprint S004."]
}
```
