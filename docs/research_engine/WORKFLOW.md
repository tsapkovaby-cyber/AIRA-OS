# Research Engine Workflow

## Operating Rules

- Research only.
- No publishing.
- No final conclusions.
- No autonomous scheduling in Sprint 005.
- No scraping, browser automation, API integrations, background workers, or AI summarization.

## Workflow

1. A research item is created from a permitted external or internal observation.
2. Required metadata is validated.
3. The source category maps to a trust level.
4. The item is normalized.
5. Freshness is computed from the publication date.
6. Duplicates are linked without deletion.
7. Conflicts are recorded without automatic resolution.
8. Confidence and research score are calculated.
9. A `KnowledgeCandidate` is produced for the Knowledge Engine.

## Example

```python
from datetime import date
from aira_os.research_engine.models import InformationCategory, SecurityContext, Source, SourceCategory, ResearchItem
from aira_os.research_engine import ResearchAPI

api = ResearchAPI()
item = ResearchItem(
    title="Example AI API release",
    summary="Official documentation describes a new API capability.",
    source=Source("Example Docs", "https://example.com/docs", SourceCategory.OFFICIAL, verified=True),
    author="Example Company",
    publication_date=date.today(),
    language="en",
    category=InformationCategory.API,
    tags={"AI API", "release"},
    security=SecurityContext(owner="research", visibility="internal"),
)
api.create_item(item)
candidate = api.forward_candidate(item.item_id)
```
