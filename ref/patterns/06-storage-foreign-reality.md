# Pattern 06: Storage (Foreign Reality)

## The Principle
The Database is just another External System. It is a **Foreign Reality** that must be explicitly modeled and translated, just like a 3rd-party API. The Domain does not define "Repositories"; it defines **Foreign Models** representing the stored data shape.

## The Mechanism
1.  **Foreign Models (Schema):** The Domain defines `DbOrder` (Pydantic) representing the SQL table structure.
2.  **Self-Translation:** `DbOrder` knows how to convert itself into `Order` (Internal Truth).
3.  **Orchestrator Execution:** The Orchestrator executes the query, validates into `DbOrder`, and translates to `Order`.

---

## 1. The Repository Abstraction (Anti-Pattern)
Traditional "Repository Patterns" hide translation logic, coupling the Domain to an interface that mimics a collection.

### ❌ Anti-Pattern: The Magic Repo
```python
order = repo.get(order_id)  # ❌ Hidden translation, hidden query
```

---

## 2. The Foreign Model (The Database Schema)
We model the database row explicitly. This lives in the Domain because knowing the persistence shape is Domain Knowledge.

### ✅ Pattern: The DB Model
```python
from pydantic import BaseModel

class DbOrder(BaseModel):
    """Foreign Model: Represents the 'orders' table."""
    model_config = {"frozen": True}
    
    id: OrderId
    status: OrderStatus
    amount_cents: int
    
    def to_domain(self) -> Order:
        return Order(
            id=self.id,
            status=self.status,
            amount=Money.from_cents(self.amount_cents),
        )
```

---

## 3. Query Result (Sum Type)
Model the query result explicitly—found or not found.

### ✅ Pattern: Explicit Result
```python
from enum import StrEnum

class StorageResultKind(StrEnum):
    FOUND = "found"
    NOT_FOUND = "not_found"

class OrderFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[StorageResultKind.FOUND]
    order: Order

class OrderNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[StorageResultKind.NOT_FOUND]
    order_id: OrderId

type FetchOrderResult = OrderFound | OrderNotFound
```

---

## 4. The Store Executor

The "Store" is a Service Layer concept (Interpreter), not a Domain concept. It executes Load/Save Intents.

### ✅ Pattern: Intent-Based Execution
```python
# service/order.py (NOT domain)
class OrderExecutor:
    """Service Class: Wiring and Execution."""
    def __init__(self, table_name: TableName):
        self.table_name = table_name
    
    async def execute_load(self, intent: LoadOrderIntent, db: AsyncSession) -> FetchOrderResult:
        # 1. Raw I/O
        result = await db.execute(select(self.table_name).where(id=intent.order_id))
        row = result.first()
        
        # 2. Pure Translation
        if not row:
            return OrderNotFound(kind=StorageResultKind.NOT_FOUND, order_id=intent.order_id)
            
        return OrderFound(
            kind=StorageResultKind.FOUND, 
            order=DbOrder.model_validate(row).to_domain()
        )
```

---

## 5. The Orchestrator (Service Class)

The Orchestrator coordinates the flow: Intent -> Executor -> Result.

### ✅ Pattern: Reactive Data Flow
```python
class OrderProcessor:
    """Service Class: Orchestration."""
    def __init__(self, executor: OrderExecutor):
        self.executor = executor
    
    async def process(self, intent: LoadOrderIntent, db: AsyncSession) -> ProcessResult:
        # 1. Execute Load Intent
        fetch_result = await self.executor.execute_load(intent, db)
        
        match fetch_result:
            case OrderFound(order=order):
                return ProcessSuccess(order=order)
            case OrderNotFound():
                return ProcessFailure("Not Found")
```

---

## 6. Why No Repository Class?
By removing the Repository Class:
1.  **Visible I/O:** You see exactly what query runs.
2.  **Explicit Translation:** The `.to_domain()` proves boundary crossing.
3.  **No Mocking:** Test Logic with `Order` objects directly.

---

## Cognitive Checks
- [ ] **Schema in Domain:** Does `domain/context/store.py` exist with Pydantic models?
- [ ] **No SQL in Domain:** The Domain defines the shape, never imports `sqlalchemy`.
- [ ] **Explicit Translation:** Does it read `DbOrder.model_validate(row).to_domain()`?
- [ ] **No Implicit None:** Is "not found" an explicit `OrderNotFound` type?
- [ ] **Store as Executor:** Is the store in `service/` not `domain/`?
- [ ] **Domain is Passive:** Does the Domain describe data, not fetch it?
- [ ] **Smart Enums:** Am I using `StorageResultKind` instead of literal "found"?
