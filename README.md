# AIRA-OS

AIRA-OS contains the architecture-first foundation for AIRA Core.

## Sprint 002 Scope

This repository currently defines eight architecture-only core modules:

- Identity Engine
- Decision Engine
- Memory Engine
- Knowledge Engine
- Research Engine
- Content Engine
- Guardian Engine
- Growth Engine

The implementation is intentionally limited to interfaces, configuration models, initialization, and documentation. No AI provider, social network, database, API integration, or business logic is included.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```
