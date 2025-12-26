from pydantic import BaseModel


class User(BaseModel):
    def check(self):
        try:  # Violation: Try/Except in Domain
            pass
        except Exception:
            pass
