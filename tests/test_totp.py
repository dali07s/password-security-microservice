
import pyotp

from app.services.totp_service import (
    generate_totp_secret,
    verify_totp_code
)


def test_secret_generation():
    secret = generate_totp_secret()

    assert len(secret) == 32


def test_valid_totp_code():
    secret = generate_totp_secret()

    totp = pyotp.TOTP(secret)
    code = totp.now()

    assert verify_totp_code(secret, code) is True


def test_invalid_totp_code(monkeypatch):
    monkeypatch.setattr(
        "app.services.totp_service.pyotp.TOTP.verify",
        lambda self, code, valid_window=0: False
    )

    secret = generate_totp_secret()
    assert verify_totp_code(
        secret,
        "000000"
    ) is False
