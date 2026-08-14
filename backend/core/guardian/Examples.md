# Guardian Engine Examples

```python
from backend.core.guardian import GuardianConfig, GuardianEngine

config = GuardianConfig(engine_name="${GUARDIAN_ENGINE_NAME}", required_environment_key="GUARDIAN_ENGINE_NAME")
engine = GuardianEngine(config)
engine.initialize()
```
