# Examples

```python
claim = EvidenceClaim("claim-1", "Feature X is documented", ClaimKind.FACT,
                      source_ids=("source-1",), research_ids=("research-1",),
                      knowledge_ids=("node-1",))
source = SourceReference("source-1", "https://vendor.example/docs", "Vendor docs")
brief = ContentBrief(topic="Feature X", why_now="Verified release", audience="Beginners",
    problem="Unclear use", main_insight="Use X for bounded tasks", evidence=(claim,),
    content_goal="Educate", platform="telegram", format="guide", tone="calm",
    cta="Save this workflow.", sources=(source,))
```

Pass this brief and a `ContentRequest` to `ContentService.create_draft`. The returned item is private and in `DRAFT`; it cannot self-approve or publish.
