from fastapi.testclient import TestClient
from app.main import app
import uuid
import pyotp

from app.core.database import SessionLocal
from app.core.crypto import decrypt_secret
from app.models.totp_account import TOTPAccount

client = TestClient(app)


def test_strength_endpoint():

    response = client.post(
        "/api/password/strength",
        json={"password": "Hello123!"}
    )

    assert response.status_code == 200
    assert "score" in response.json()


def test_generator_endpoint():

    response = client.post(
        "/api/password/generate",
        json={"length": 16}
    )

    assert response.status_code == 200
    assert len(response.json()["password"]) == 16


def test_generator_rejects_invalid_length():

    response = client.post(
        "/api/password/generate",
        json={"length": 3}
    )

    assert response.status_code == 422


def test_passphrase_endpoint():

    response = client.post(
        "/api/passphrase/generate",
        json={"number_of_words": 5}
    )

    assert response.status_code == 200
    assert len(response.json()["passphrase"].split("-")) == 5



def test_totp_setup_endpoint():
    username = "test_" + uuid.uuid4().hex[:8]

    response = client.post(
        "/api/2fa/setup",
        json={"username": username}
    )

    assert response.status_code == 200

    data = response.json()

    assert "qr_code_base64" in data
    assert "secret" not in data
    assert data["username"] == username
def test_security_headers():

    response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"  


 
def test_totp_complete_workflow():
    username = "api_test_" + uuid.uuid4().hex[:8]

    # Step 1: Register the TOTP account
    setup_response = client.post(
        "/api/2fa/setup",
        json={"username": username}
    )

    assert setup_response.status_code == 200

    setup_data = setup_response.json()

    assert "qr_code_base64" in setup_data
    assert "secret" not in setup_data

    # Step 2: Retrieve the encrypted secret from the database
    db = SessionLocal()

    try:
        account = db.query(TOTPAccount).filter_by(
            username=username
        ).first()

        assert account is not None

        secret = decrypt_secret(account.secret_encrypted)

        # Step 3: Generate a valid authenticator code
        code = pyotp.TOTP(secret).now()

        # Step 4: Verify the code through the API
        verify_response = client.post(
            "/api/2fa/verify",
            json={
                "username": username,
                "code": code
            }
        )

        assert verify_response.status_code == 200
        assert verify_response.json()["verified"] is True

        db.refresh(account)

        assert account.enabled is True

    finally:
        db.query(TOTPAccount).filter_by(
            username=username
        ).delete()
        db.commit()
        db.close()
def test_generator_rejects_too_short_password():
    response = client.post(
        "/api/password/generate",
        json={"length": 3}
    )

    assert response.status_code == 422


def test_generator_rejects_too_long_password():
    response = client.post(
        "/api/password/generate",
        json={"length": 129}
    )

    assert response.status_code == 422


def test_strength_rejects_empty_password():
    response = client.post(
        "/api/password/strength",
        json={"password": ""}
    )

    assert response.status_code == 422


def test_totp_rejects_invalid_code_format():
    response = client.post(
        "/api/2fa/verify",
        json={
            "username": "student01",
            "code": "abc"
        }
    )

    assert response.status_code == 422


def test_totp_rejects_unknown_username():
    response = client.post(
        "/api/2fa/verify",
        json={
            "username": "unknown_student_123",
            "code": "123456"
        }
    )

    assert response.status_code == 404   