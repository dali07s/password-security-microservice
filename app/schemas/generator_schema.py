from pydantic import BaseModel, Field


class PasswordGeneratorRequest(BaseModel):
    length: int = Field(
        ge=4,
        le=128,
        description="Password length (4 to 128)",
        examples=[16]
    )