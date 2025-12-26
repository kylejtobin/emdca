---
description: "Pattern 06: Storage — Database as Foreign Reality with explicit translation."
globs: ["**/domain/**/*.py", "**/service/**/*.py"]
alwaysApply: false
---

# Pattern 06: Storage Foreign Reality

## Valid Code Structure

```python
class StorageResultKind(StrEnum):
    FOUND = "found"
    NOT_FOUND = "not_found"

class IntentKind(StrEnum):
    LOAD_ORDER = "load_order"

# Foreign Model: Represents the database row shape
class DbOrder(BaseModel):
    model_config = {"frozen": True}
    
    id: OrderId
    status: OrderStatus
    amount_cents: PositiveInt
    
    def to_domain(self) -> Order:
        return Order(
            id=self.id,
            status=self.status,
            amount=Money.from_cents(self.amount_cents),
        )

# Query Result: Explicit Sum Type
class OrderFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[StorageResultKind.FOUND]  # NO DEFAULT
    order: Order

class OrderNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[StorageResultKind.NOT_FOUND]  # NO DEFAULT
    order_id: OrderId

type FetchOrderResult = OrderFound | OrderNotFound

# Intent (Domain)
class LoadOrderIntent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[IntentKind.LOAD_ORDER]
    order_id: OrderId

# Executor: Service Layer (Regular Class)
class OrderExecutor:
    def __init__(self, table_name: TableName):
        self.table_name = table_name
    
    async def execute_load(self, intent: LoadOrderIntent, db: Any) -> FetchOrderResult:
        # 1. I/O
        row = await db.fetch_one(intent.order_id)
        
        # 2. Translation
        if not row:
            return OrderNotFound(kind=StorageResultKind.NOT_FOUND, order_id=intent.order_id)
        return OrderFound(
            kind=StorageResultKind.FOUND, 
            order=DbOrder.model_validate(row).to_domain()
        )
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| `DbModel` with `.to_domain()` method | Repository pattern with abstract interface |
| `Found \| NotFound` Sum Type | `return None` for not found |
| **Store as Executor (Service Layer)** | **Store as Class in Domain** |
| **Domain returns Intent to Load** | **Domain calls Store.fetch()** |
| `DbOrder.model_validate(row).to_domain()` | Raw dict passing |
| **Executor is a Regular Class** | **Executor is a Pydantic Model or Dataclass** |
| **Typed IDs (OrderId)** | **String IDs (str)** |
| **Smart Enums for Kinds** | **String Literals for Kinds** |
