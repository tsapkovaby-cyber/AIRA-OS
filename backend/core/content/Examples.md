# Content Engine Examples

```python
from backend.core.content import ContentConfig, ContentEngine

config = ContentConfig(engine_name="${CONTENT_ENGINE_NAME}", required_environment_key="CONTENT_ENGINE_NAME")
engine = ContentEngine(config)
engine.initialize()
```
