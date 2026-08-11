# Decision Engine Examples

```python
from backend.core.decision import DecisionConfig, DecisionEngine

config = DecisionConfig(engine_name="${DECISION_ENGINE_NAME}", required_environment_key="DECISION_ENGINE_NAME")
engine = DecisionEngine(config)
engine.initialize()
```
