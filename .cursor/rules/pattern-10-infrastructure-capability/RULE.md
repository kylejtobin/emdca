---
description: "Pattern 10: Infrastructure — Capability as Data. Domain declares abstract needs, Service binds to technology."
globs: ["**/service/**/*.py", "**/domain/**/store.py", "**/domain/**/failure.py"]
alwaysApply: false
---

# Pattern 10: Infrastructure Capability as Data

## Valid Code Structure

```python
# DOMAIN: Configuration (Data), not Behavior (Methods)
class EventCapability(BaseModel):
    """Abstract capability: I need a topic with these params."""
    model_config = {"frozen": True}
    topic_name: TopicName
    retention_days: PositiveInt

# DOMAIN: Intent (Data)
class StoreEventIntent(BaseModel):
    """I want to store this."""
    model_config = {"frozen": True}
    kind: Literal[EventIntentKind.STORE]
    event_data: EventPayload

# SERVICE: Executor (Service Class)
class EventExecutor:
    """Binds Capability (Config) to Technology."""
    
    def __init__(self, capability: EventCapability, client: NatsClient):
        self.capability = capability
        self.client = client
    
    async def execute(self, intent: StoreEventIntent) -> EventResult:
        # Use Config to direct the Action
        topic = self.capability.topic_name
        
        try:
            await self.client.publish(topic, intent.event_data)
            return EventStored(kind=EventResultKind.STORED)
        except NatsError:
            return EventFailed(kind=EventResultKind.FAILED)
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Domain declares **Configuration Data** | `import boto3` / `import nats` in domain |
| Failure modes as abstract `StrEnum` | Technology-specific configs in domain |
| Service layer owns tech configs | `NatsStreamConfig` in `domain/` |
| **Service executes Intents** | **Service implements Interfaces** |
| All fields explicit, no defaults | Side effects on model init |
| **Capabilities are Data (Specs)** | **Capabilities are Interfaces (Methods)** |
| **Executor is a Service Class** | **Executor is a Pydantic Model** |
