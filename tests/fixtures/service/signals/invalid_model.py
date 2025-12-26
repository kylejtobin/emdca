from pydantic import BaseModel


class UserExecutor(BaseModel):  # Violation: Service as Model
    model_config = {"frozen": True}

    def execute(self):
        pass
