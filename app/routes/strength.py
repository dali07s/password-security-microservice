
from fastapi import APIRouter

from app.schemas.password_schema import PasswordRequest
from app.services.strength_service import analyze_password

router = APIRouter()


@router.post(
    "/strength",
    summary="Analyze Password Strength",
    description="""
    Evaluates a password using zxcvbn.

    Returns its estimated strength score, length,
    character diversity and feedback.
    """,
    response_description="Password strength analysis result",
    responses={
        200: {
            "description": "Password analyzed successfully"
        },
        422: {
            "description": "Invalid request body"
        }
    }
)
def check_strength(request: PasswordRequest):
    result = analyze_password(request.password)
    return result