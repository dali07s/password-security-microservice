
from pydantic import BaseModel, Field


class TOTPSetupRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username to enroll in TOTP",
        examples=["student01"]
    )


class TOTPVerifyRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        examples=["student01"]
    )

    code: str = Field(
        pattern=r"^\d{6}$",
        description="Current six-digit authenticator code",
        examples=["123456"]
    )