from pydantic import BaseModel, Field


class BreachCheckRequest(BaseModel):
    password: str = Field(
        min_length=1,
        max_length=128,
        description="Password to check for known exposure",
        examples=["MyPassword123!"]
    )