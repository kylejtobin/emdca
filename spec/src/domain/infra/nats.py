"""
THE INFRASTRUCTURE CAPABILITY (NATS)

Role: Defines Capability Models and Executors for NATS.
Mandate: Mandate X (Infra as Data) & IV (Intent).
Pattern: spec/patterns/10-infrastructure-capability-as-data.md
Pattern: spec/patterns/04-execution-intent.md

Constraint:
- Capability Models mirror what NATS expects (interface contracts).
- Executors are frozen Pydantic models that perform I/O and return Sum Types.
- No exception catching in domain — infrastructure returns Sum Types.

Example Implementation:
```python
from pydantic import BaseModel
from typing import Literal

# Capability Model (what NATS expects)
class NatsStreamConfig(BaseModel):
    model_config = {"frozen": True}
    name: str
    subjects: tuple[str, ...]
    retention: Literal["limits", "interest", "workqueue"]
    max_msgs: int
    max_bytes: int

# Result Sum Types (what infrastructure returns)
class Connected(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["connected"]
    client: object  # The actual NATS client

class ConnectionFailed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["connection_failed"]
    error: str

type ConnectResult = Connected | ConnectionFailed

# Executor (frozen model with connect logic)
class NatsConnector(BaseModel):
    model_config = {"frozen": True}
    url: str

    async def connect(self) -> ConnectResult:
        \"\"\"Infrastructure edge: performs I/O, returns Sum Type.\"\"\"
        # Shell code here catches exceptions, returns Sum Type
        ...
```
"""
