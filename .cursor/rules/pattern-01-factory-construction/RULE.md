---
description: "Pattern 01: Construction — Parse, don't validate. Factory methods on frozen models."
globs: ["**/domain/**/*.py", "**/entity.py"]
alwaysApply: false
---

# Pattern 01: Factory Construction

## Valid Code Structure

```python
# Smart Enum
class CreationResultKind(StrEnum):
    CREATED = "created"
    REJECTED = "rejected"

# Value Objects: Use Pydantic built-ins
class User(BaseModel):
    model_config = {"frozen": True}
    email: EmailStr
    age: PositiveInt = Field(ge=18)  # Structural Constraint!

# Result Types: Explicit success/failure
class UserCreated(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[CreationResultKind.CREATED]
    user: User

class UserRejected(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[CreationResultKind.REJECTED]
    reason: RejectionReason

type CreateUserResult = UserCreated | UserRejected

# Factory: Pure Construction (Crash on Failure)
class UserFactory:
    @staticmethod
    def create(raw: dict) -> CreateUserResult:
        # Pydantic handles validation. If it fails, it crashes.
        # This is correct. The system does not accept invalid input.
        return UserCreated(
            kind=CreationResultKind.CREATED,
            user=User.model_validate(raw)
        )
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| `model_config = {"frozen": True}` | Default values on fields |
| `EmailStr`, `PositiveInt` (Pydantic built-ins) | `str`, `int` for domain concepts |
| **Factory simply calls model_validate** | **Factory manual if/else checks** |
| **Constraint encoded in Type** | **Constraint encoded in Factory Logic** |
| Crash on invalid input | `try/except` inside Domain |
| **Smart Enums for Kinds** | **String Literals** |
