import pyotp
import qrcode
import base64
from io import BytesIO


def generate_totp_secret():

    return pyotp.random_base32()


def generate_totp_qr(secret: str, username: str):

    totp = pyotp.TOTP(secret)

    uri = totp.provisioning_uri(
        name=username,
        issuer_name="Password Security Microservice"
    )

    qr = qrcode.make(uri)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return qr_base64


def verify_totp_code(secret: str, code: str):

    try:
        totp = pyotp.TOTP(secret)
        return bool(totp.verify(code, valid_window=1))
    except Exception:
        return False