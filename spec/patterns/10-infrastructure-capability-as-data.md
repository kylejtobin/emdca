# Pattern 10: Infrastructure (Capability as Data)

## The Principle
Infrastructure has a shape. Model it. What a stream looks like, what a bucket requires, what an agent configuration expects—these are **interface contracts** the Domain owns as Pydantic models. The Shell resolves these models against real infrastructure.

## The Mechanism
1. **Capability Models:** Pydantic models mirror what infrastructure systems expect (stream configs, bucket policies, agent topologies)
2. **Failure Models:** Smart Enums enumerate how infrastructure can fail
3. **Shell Resolution:** The Shell reads capability models and provisions real infrastructure

The Domain never imports infrastructure libraries. It declares the shape of what should exist.

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

## ✅ Pattern: Capability Model (Messaging)

Model what the messaging system expects.

```python
class NatsStreamConfig(BaseModel):
    """Models what NATS expects when creating a stream."""
    model_config = {"frozen": True}
    
    name: str
    subjects: tuple[str, ...]
    retention: Literal["limits", "interest", "workqueue"]
```

---

## ✅ Pattern: Capability Model (Storage)

Model what the storage system expects.

```python
class S3BucketConfig(BaseModel):
    """Models what S3 expects when creating a bucket."""
    model_config = {"frozen": True}
    
    name: str
    region: str
    versioning: Literal["enabled", "suspended"]
```

---

## ✅ Pattern: Failure Model

Model how infrastructure can fail. The Domain declares failure modes; the Shell maps them to real exceptions.

```python
class InfraFailure(StrEnum):
    """How infrastructure can fail."""
    TIMEOUT = "timeout"
    CONNECTION_CLOSED = "connection_closed"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    # ...
```

---

## ✅ Pattern: Capability in Intent

Capability models feed into Intents (Pattern 04). The Intent references the capability; execution is separate.

```python
class EnsureStreamIntent(BaseModel):
    """Intent that uses a capability model."""
    model_config = {"frozen": True}
    kind: Literal["ensure_stream"]
    
    config: NatsStreamConfig  # Capability model
    handled_failures: tuple[InfraFailure, ...]  # Failure model
```

---

## Shell Resolution

The Shell receives capability models and provisions real infrastructure. Execution follows Pattern 04—the Shell composes models, never catches exceptions in domain logic.

---

## Cognitive Checks

- [ ] **No Libraries in Domain:** Did I remove `import boto3` from the `domain/` folder?
- [ ] **Capability is a Model:** Is infrastructure shape a `BaseModel`, not a plain dict?
- [ ] **Failures are Enumerated:** Is failure a `StrEnum`, not raw strings?
- [ ] **No Default Values:** Are all fields explicit at construction?
