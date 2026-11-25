from fastapi import APIRouter
from app.schemas.generator_schema import PasswordGeneratorRequest
from app.services.generator_service import generate_password

router = APIRouter()


@router.post(
    "/generate",
    summary="Generate Secure Password",
    description="""
    Generates a random password using Python's secrets module.

    The requested length must be between 4 and 128 characters.
    The generated password contains lowercase, uppercase,
    numeric and symbol characters.
    """,
    response_description="Generated password and its length",
    responses={
        200: {
            "description": "Password generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "password": "aB7!xP9#mK2@qL5$",
                        "length": 16
                    }
                }
            }
        },
        422: {
            "description": "Invalid password length"
        }
    }
)
def generate(request: PasswordGeneratorRequest):
    password = generate_password(request.length)
    return {"password": password, "length": len(password)}