"""
THE INFRASTRUCTURE CAPABILITY (Redis)

Role: Defines Capability Models and Executors for Redis.
Mandate: Mandate X (Infra as Data) & IV (Intent).
Pattern: spec/patterns/10-infrastructure-capability-as-data.md
Pattern: spec/patterns/04-execution-intent.md

Constraint:
- Capability Models mirror what Redis expects (interface contracts).
- Executors are frozen Pydantic models that perform I/O and return Sum Types.
- No exception catching in domain — infrastructure returns Sum Types.
- No `| None` — use Sum Types for distinct states.

Example Implementation:
```python
from pydantic import BaseModel
from typing import Literal

# Result Sum Types (explicit states, no None)
class ValueFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["found"]
    key: str
    value: bytes

class KeyNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["not_found"]
    key: str

class GetFailed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["failed"]
    key: str
    error: str

type GetResult = ValueFound | KeyNotFound | GetFailed

# Executor (frozen model with Redis connection as field)
class RedisClient(BaseModel):
    model_config = {"frozen": True}
    connection: object  # Redis connection

    async def get(self, key: str) -> GetResult:
        \"\"\"Infrastructure edge: performs I/O, returns Sum Type.\"\"\"
        # Shell code here catches exceptions, returns Sum Type
        ...
```
"""
