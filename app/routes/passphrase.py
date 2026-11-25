from fastapi import APIRouter

from app.schemas.passphrase_schema import PassphraseRequest

from app.services.passphrase_service import generate_passphrase


router = APIRouter()


@router.post(
    "/generate",
    summary="Generate Memorable Passphrase",
    description="""
    Generates a human-memorable passphrase by randomly
    selecting words from the EFF Diceware wordlist.

    The number of words must be between 4 and 10.
    """,
    response_description="Generated passphrase",
    responses={
        200: {
            "description": "Passphrase generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "passphrase": "correct-horse-battery-example",
                        "number_of_words": 4
                    }
                }
            }
        },
        422: {
            "description": "Invalid number of words"
        }
    }
)
def create_passphrase(request: PassphraseRequest):
    passphrase = generate_passphrase(request.number_of_words)
    return {
        "passphrase": passphrase,
        "number_of_words": request.number_of_words
    }