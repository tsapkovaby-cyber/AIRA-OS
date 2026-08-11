# Research Engine Examples

```python
from backend.core.research import ResearchConfig, ResearchEngine

config = ResearchConfig(engine_name="${RESEARCH_ENGINE_NAME}", required_environment_key="RESEARCH_ENGINE_NAME")
engine = ResearchEngine(config)
engine.initialize()
```
