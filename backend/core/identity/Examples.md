# Identity Engine Examples

```python
from backend.core.identity import IdentityConfig, IdentityEngine

config = IdentityConfig(engine_name="${IDENTITY_ENGINE_NAME}", required_environment_key="IDENTITY_ENGINE_NAME")
engine = IdentityEngine(config)
engine.initialize()
```
