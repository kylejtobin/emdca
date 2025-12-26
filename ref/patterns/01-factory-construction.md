# Pattern 01: Construction (The Pure Factory)

## The Principle
Validation is not a check; it is a construction process. Logic is a calculation, not an action. Therefore, the code that makes decisions must be separated from the code that executes them.

## The Mechanism
All data enters the domain through **Pure Factory Methods** (or direct `model_validate` calls). We rely on **Correctness by Construction**. If data does not fit the type, construction fails (crashes/raises). We do not "handle" invalid input in the domain; we reject it at the boundary.

---

## 1. The Foundation: Value Objects
Before constructing entities, we must parse primitives into **Value Objects** that carry structural proofs of validity. Primitive Obsession (passing raw strings) is forbidden.

### ❌ Anti-Pattern: Primitive Obsession with Runtime Checks
```python
class User(BaseModel):
    email: str
    
    def validate(self):
        if "@" not in self.email:
            raise ValueError("Invalid email")  # ❌ Runtime check, not construction
```

### ✅ Pattern: Valid-By-Construction Types
Use Pydantic's built-in types. No hand-rolled validators.

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    model_config = {"frozen": True}
    
    id: UserId
    email: EmailStr  # Pydantic built-in—guarantees validity
```

---

## 2. The Pure Factory: Constraint by Type
We do not write `if` statements to check data. We define Types that enforce constraints.

### ❌ Anti-Pattern: Manual Logic
```python
def create_user(data: dict) -> User:
    if data['age'] < 18:
        raise ValueError("Too young")  # ❌ Logic disguised as validation
    return User(**data)
```

### ✅ Pattern: Structural Constraints
The Type itself enforces the rule. The Factory just attempts to build it.

```python
from enum import StrEnum
from pydantic import BaseModel, Field, EmailStr

class CreationResultKind(StrEnum):
    CREATED = "created"
    REJECTED = "rejected"

# 1. Define the Constraint
class AdultAge(BaseModel):
    model_config = {"frozen": True}
    # The rule is here, not in code
    value: int = Field(ge=18)

class User(BaseModel):
    model_config = {"frozen": True}
    email: EmailStr
    age: AdultAge

# 2. The Factory (Pass-through)
class UserFactory:
    """Namespace for factory logic."""
    
    @staticmethod
    def create(raw: dict) -> User:
        # We blindly attempt construction.
        # If raw['age'] is 15, Pydantic raises ValidationError.
        # The System crashes (rejects input). This is correct.
        return User.model_validate(raw)
```

---

## Cognitive Checks
- [ ] **No Validation Methods:** Did I remove `.validate()` or `.check()`?
- [ ] **No Manual Ifs:** Did I remove `if age < 18`?
- [ ] **Type Constraints:** Is the rule encoded in `Field(...)` or a Value Object?
- [ ] **Frozen Models:** Is `model_config = {"frozen": True}` everywhere?
- [ ] **Crash on Invalid:** Do I allow Pydantic to raise `ValidationError`?
- [ ] **Pure Class:** Is the factory a plain class or static method?
- [ ] **Smart Enums:** Am I using `CreationResultKind`?
