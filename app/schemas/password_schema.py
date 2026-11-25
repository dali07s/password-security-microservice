from pydantic import BaseModel, Field


class PasswordRequest(BaseModel):
    password: str = Field(
        min_length=1,
        max_length=128,
        description="Password to analyze",
        examples=["MyPassword123!"]
    )