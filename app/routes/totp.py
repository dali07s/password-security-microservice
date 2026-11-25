
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import pyotp

from app.core.database import get_db
from app.core.crypto import encrypt_secret, decrypt_secret
from app.core.limiter import limiter
import time
from app.models.totp_account import TOTPAccount
from app.schemas.totp_schema import (
    TOTPSetupRequest,
    TOTPVerifyRequest
)

from app.services.totp_service import (
    generate_totp_secret,
    generate_totp_qr
)

router = APIRouter()


@router.post(
    "/setup",
    summary="Set Up Two-Factor Authentication",
    description="""
    Creates a TOTP secret for a username, encrypts and saves
    it in the database, and returns a Base64-encoded QR code.

    Scan the QR code with a compatible authenticator application.
    The raw secret is not returned separately.
    """,
    response_description="TOTP enrollment QR code",
    responses={
        200: {
            "description": "TOTP enrollment created"
        },
        409: {
            "description": "TOTP is already registered for this username"
        },
        422: {
            "description": "Invalid username"
        }
    }
)
def setup_2fa(
    request: Request,
    data: TOTPSetupRequest,
    db: Session = Depends(get_db)
):
    existing_account = db.query(TOTPAccount).filter_by(
        username=data.username
    ).first()

    if existing_account and existing_account.enabled:
        raise HTTPException(
            status_code=409,
            detail="2FA is already registered and active for this username"
        )

    secret = generate_totp_secret()
    encrypted_secret = encrypt_secret(secret)

    if existing_account:
        existing_account.secret_encrypted = encrypted_secret
        existing_account.last_used_step = None
    else:
        account = TOTPAccount(
            username=data.username,
            secret_encrypted=encrypted_secret,
            enabled=False
        )
        db.add(account)

    db.commit()

    qr_code = generate_totp_qr(secret, data.username)

    return {
        "username": data.username,
        "qr_code_base64": qr_code,
        "qr_code": f"data:image/png;base64,{qr_code}",
        "manual_key": secret,
        "message": "Scan the QR code with your authenticator app"
    }


@router.post(
    "/verify",
    summary="Verify TOTP Authentication Code",
    description="""
    Retrieves the encrypted TOTP secret associated with the username,
    decrypts it internally and verifies the submitted six-digit code.

    Limited to 5 requests per minute per client IP address.
    """,
    response_description="TOTP verification result",
    responses={
        200: {
            "description": "Verification completed; check the verified field"
        },
        404: {
            "description": "TOTP account not found"
        },
        422: {
            "description": "Invalid request or code format"
        },
        429: {
            "description": "Rate limit exceeded"
        }
    }
)
@limiter.limit("5/minute")
def verify_2fa(
    request: Request,
    data: TOTPVerifyRequest,
    db: Session = Depends(get_db)
):
    account = db.query(TOTPAccount).filter_by(
        username=data.username
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="2FA account not found"
        )

    secret = decrypt_secret(account.secret_encrypted)
    totp = pyotp.TOTP(secret)

    current_step = int(time.time() // totp.interval)
    matched_step = None

    # Accept the current period and one adjacent period
    for step in (current_step - 1, current_step, current_step + 1):
        if totp.verify(
            data.code,
            for_time=step * totp.interval
        ):
            matched_step = step
            break

    # Reject invalid or previously used codes
    if (
        matched_step is None
        or (
            account.last_used_step is not None
            and matched_step <= account.last_used_step
        )
    ):
        return {
            "verified": False,
            "message": "Invalid or previously used authentication code"
        }

    account.last_used_step = matched_step
    account.enabled = True
    db.commit()

    return {
        "verified": True,
        "message": "Authentication successful"
    }
