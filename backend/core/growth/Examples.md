# Growth Engine Examples

```python
from backend.core.growth import GrowthConfig, GrowthEngine

config = GrowthConfig(engine_name="${GROWTH_ENGINE_NAME}", required_environment_key="GROWTH_ENGINE_NAME")
engine = GrowthEngine(config)
engine.initialize()
```
