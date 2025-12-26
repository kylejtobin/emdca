from pydantic import BaseModel, EmailStr, PositiveInt


class User(BaseModel):
    model_config = {"frozen": True}
    email: EmailStr
    age: PositiveInt
