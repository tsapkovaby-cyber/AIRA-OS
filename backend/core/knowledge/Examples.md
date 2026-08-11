# Knowledge Engine Examples

```python
from backend.core.knowledge import KnowledgeConfig, KnowledgeEngine

config = KnowledgeConfig(engine_name="${KNOWLEDGE_ENGINE_NAME}", required_environment_key="KNOWLEDGE_ENGINE_NAME")
engine = KnowledgeEngine(config)
engine.initialize()
```
