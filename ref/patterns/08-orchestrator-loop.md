# Pattern 08: Coordination (The Orchestrator)

## The Principle
A system needs a "driver" that does no thinking, only moving. It coordinates the flow of data between models and execution shell. We call this the **Runtime** or **Orchestrator**.

## The Mechanism
The **Runtime** is a Service Class (not a Model). It runs a "dumb" reactive loop: Load → Step → Save → Execute. It contains no business rules, only flow control.

---

## 1. The Fat Service (Anti-Pattern)
Putting business logic ("Thinking") inside the orchestration layer ("Moving") makes the system rigid and hard to test.

### ❌ Anti-Pattern: Logic in the Loop
```python
def process_payment(payment_id: str, db: Session):  # ❌ Standalone function
    payment = fetch_payment(db, payment_id)
    
    if payment.amount > 10000 and not payment.is_verified:  # ❌ Business logic leak
        raise ValueError("Large payments need verification")  # ❌ Exception for logic
```

---

## 2. The Runtime (Service Class)

The Runtime drives the State Machine. It does not decide; it merely executes the Domain's decisions.

### ✅ Pattern: The Reactive Loop
```python
from enum import StrEnum

class PaymentResultKind(StrEnum):
    NOT_FOUND = "not_found"
    PROCESSED = "processed"

class PaymentRuntime:
    """Service Class: Wiring only."""
    
    def __init__(self, executor: PaymentExecutor):
        self.executor = executor
    
    def run(self, payment_id: PaymentId, event: PaymentEvent) -> ProcessPaymentResult:
        # 1. Load State (Generic I/O)
        state = self.executor.load(payment_id)
        
        # Handle "Not Found" as a valid result track
        if not state:
            return PaymentNotFound(kind=PaymentResultKind.NOT_FOUND, payment_id=payment_id)
        
        # 2. Pure Step (Domain Logic)
        # The Domain Model (PaymentState) owns the decision.
        new_state, intent = state.handle(event)
        
        # 3. Save State (Generic I/O)
        self.executor.save(payment_id, new_state)
        
        # 4. Execute Intent (Generic I/O)
        self.executor.execute(intent)
        
        return PaymentProcessed(kind=PaymentResultKind.PROCESSED, payment_id=payment_id)
```

---

## 3. Transaction Boundaries
The Runtime is responsible for the **Unit of Work**. Wrap in transaction context.

### ✅ Pattern: Explicit Transactions
```python
class TransactionalRuntime:
    """Runtime with transaction boundary."""
    
    def __init__(self, runtime: PaymentRuntime):
        self.runtime = runtime
    
    def run_safely(self, payment_id: PaymentId, db: Session) -> ProcessPaymentResult:
        with db.begin():
            return self.runtime.run(payment_id, db)
```

---

## Cognitive Checks
- [ ] **Dependencies as Fields:** Are executors injected via `__init__`?
- [ ] **No If Statements:** Does the runtime contain `if payment.amount > X`? (Move to Domain)
- [ ] **Runtime is Class:** Is it a regular `class`, NOT a `BaseModel`?
- [ ] **Step Delegation:** Does it call `state.handle()` or `state.step()`?
- [ ] **Side Effects via Intent:** Does it execute intents returned by the domain?
- [ ] **No Magic Strings:** Are result kinds defined as Smart Enums?
- [ ] **Value Objects:** Am I using `PaymentId` instead of `str`?
