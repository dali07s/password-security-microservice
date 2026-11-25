import requests
from fastapi import APIRouter, HTTPException, Request

from app.schemas.breach_schema import BreachCheckRequest
from app.services.breach_service import check_password_breach
from app.core.limiter import limiter

router = APIRouter()


@router.post(
    "/breach-check",
    summary="Check Password Against Known Breaches",
    description="""
    Checks whether a password appears in the Have I Been Pwned
    Pwned Passwords database using the k-anonymity model.

    The password is hashed locally using SHA-1.
    Only the first five characters of the hash are sent
    to the external service.

    Limited to 10 requests per minute per client IP address.
    """,
    response_description="Password breach analysis",
    responses={
        200: {
            "description": "Breach lookup completed"
        },
        422: {
            "description": "Invalid request body"
        },
        429: {
            "description": "Rate limit exceeded"
        },
        503: {
            "description": "External breach checking service unavailable"
        }
    }
)
@limiter.limit("10/minute")
def breach_check(
    request: Request,
    data: BreachCheckRequest
):
    try:
        result = check_password_breach(data.password)
        return result
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Breach checking service is temporarily unavailable"
        )