# Memory Engine Examples

```python
from backend.core.memory import MemoryConfig, MemoryEngine

config = MemoryConfig(engine_name="${MEMORY_ENGINE_NAME}", required_environment_key="MEMORY_ENGINE_NAME")
engine = MemoryEngine(config)
engine.initialize()
```
