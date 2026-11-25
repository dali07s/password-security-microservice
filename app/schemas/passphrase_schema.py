from pydantic import BaseModel, Field


class PassphraseRequest(BaseModel):
    number_of_words: int = Field(
        ge=4,
        le=10,
        description="Number of words in the passphrase",
        examples=[5]
    )