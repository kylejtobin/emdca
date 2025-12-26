---
description: "Pattern 08: Coordination — Dumb Orchestrator that moves data, doesn't think."
globs: ["**/service/**/*.py", "**/orchestrator.py"]
alwaysApply: false
---

# Pattern 08: Orchestrator Loop

## Valid Code Structure

```python
# Result Types (Smart Enum)
class PaymentResultKind(StrEnum):
    NOT_FOUND = "not_found"
    PROCESSED = "processed"
    VERIFICATION_REQUIRED = "verification_required"

class PaymentNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[PaymentResultKind.NOT_FOUND]
    payment_id: PaymentId

class PaymentProcessed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[PaymentResultKind.PROCESSED]
    payment_id: PaymentId

class VerificationRequired(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[PaymentResultKind.VERIFICATION_REQUIRED]
    reason: VerificationReason

type ProcessPaymentResult = PaymentNotFound | PaymentProcessed | VerificationRequired

# Service Class: The Runtime (Orchestrator)
class PaymentRuntime:
    """
    The Runtime drives the process.
    It loads state, steps the machine, saves state, and executes intents.
    It contains NO business logic.
    """
    def __init__(self, executor: PaymentExecutor):
        self.executor = executor

    def run(self, payment_id: PaymentId, event: PaymentEvent) -> ProcessPaymentResult:
        # 1. Load State (I/O)
        state = self.executor.load(payment_id)
        if not state:
            return PaymentNotFound(kind=PaymentResultKind.NOT_FOUND, payment_id=payment_id)

        # 2. Pure Step (Domain Logic)
        # The Domain decides what happens next.
        new_state, intent = state.handle(event)

        # 3. Save State (I/O)
        self.executor.save(payment_id, new_state)

        # 4. Execute Intent (Side Effect)
        # The Domain decided WHAT to do; the Runtime does it.
        self.executor.execute(intent)
        
        return PaymentProcessed(kind=PaymentResultKind.PROCESSED, payment_id=payment_id)
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| **Runtime is a Service Class** | **Runtime is a Pydantic Model** |
| Logic delegated to Domain `state.handle()` | Logic inside `run()` |
| **Reactive Loop Pattern** | **Procedural Script Pattern** |
| Explicit Dependencies (`executor`) | Implicit Globals |
| `match/case` for flow control | `raise` for control flow |
| **Smart Enums for Result Kinds** | **Magic Strings for Result Kinds** |
| **Typed IDs (PaymentId)** | **String IDs (str)** |
