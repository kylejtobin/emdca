# Pattern 10: Infrastructure (Capability as Data)

## The Principle
Domain contexts define abstract capabilities they need as **Configuration Data**, not interfaces. The Service layer provides the execution runtime. The Domain never "calls" infrastructure; it outputs **Intents** that the runtime executes using the configuration.

## The Mechanism
1. **Capability Config:** A Pydantic model defining the *parameters* of the capability (e.g., topic names, bucket names).
2. **Intent:** A Pydantic model describing the *desire* to use the capability (e.g., "Save this").
3. **Runtime Binding:** The Shell looks up the Config and executes the Intent.

---

## ❌ Anti-Pattern: Connection in Domain

Instantiating clients inside the domain couples logic to the runtime environment.

```python
import boto3

class StorageService:
    def __init__(self):
        self.s3 = boto3.client("s3")  # ❌ Side effect on init
```

---

## ❌ Anti-Pattern: Technology Config in Domain

Technology-specific configuration is infrastructure knowledge, not domain knowledge.

```python
# ❌ WRONG: This is NATS knowledge, not domain knowledge
# domain/infra/nats.py  <-- This file should not exist
class NatsStreamConfig(BaseModel):
    name: str
    subjects: tuple[str, ...]
    retention: Literal["limits", "interest", "workqueue"]  # NATS concept
```

---

## ✅ Pattern: Capability as Data (Configuration)

The domain declares the *parameters* it needs to operate, modeled as data.

```python
# domain/event/capability.py
class EventCapability(BaseModel):
    """Configuration: I need a place to put events."""
    model_config = {"frozen": True}
    
    topic_prefix: TopicName
    retention_days: PositiveInt

# domain/event/intent.py
class PublishEventIntent(BaseModel):
    """Intent: I want to publish an event."""
    model_config = {"frozen": True}
    kind: Literal[EventIntentKind.PUBLISH]
    
    payload: EventPayload
    stream_id: StreamId
```

---

## ✅ Pattern: Abstract Failure Model

Model how operations can fail in abstract terms. The Shell maps technology exceptions to these.

```python
# domain/event/failure.py
class EventStoreFailure(StrEnum):
    """How event operations can fail (abstract)."""
    TIMEOUT = "timeout"
    CONNECTION_LOST = "connection_lost"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
```

---

## ✅ Pattern: Runtime Execution (The Shell)

The Shell matches the Intent, looks up the Capability Config, and performs the side effect.

```python
# service/event.py
class NatsRuntime:
    """The Runtime knows how to interpret Config + Intent."""
    
    def __init__(self, capability: EventCapability, client: NatsClient):
        self.capability = capability
        self.client = client
    
    async def execute(self, intent: PublishEventIntent) -> PublishResult:
        # 1. Use Config to determine *where* (Topic)
        topic = f"{self.capability.topic_prefix}.{intent.stream_id}"
        
        # 2. Perform Side Effect (I/O)
        try:
            await self.client.publish(topic, intent.payload)
            return PublishSuccess(kind=EventResultKind.PUBLISHED)
        except NatsTimeoutError:
            return PublishFailure(kind=EventResultKind.FAILED, reason=EventStoreFailure.TIMEOUT)
```

---

## Cognitive Checks

- [ ] **No Libraries in Domain:** Did I remove `import boto3` / `import nats` from `domain/`?
- [ ] **No Tech Configs in Domain:** Is `NatsStreamConfig` / `S3BucketConfig` in `service/`, not `domain/`?
- [ ] **Domain is Data:** Does domain declare *Configuration*, not *Interfaces*?
- [ ] **Failures are Abstract:** Are failure modes tech-agnostic (timeout, not NatsTimeout)?
- [ ] **Service Executes:** Does the service layer execute Intents?
- [ ] **Typed Config:** Am I using `TopicName`, not `str`?
