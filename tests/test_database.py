
import uuid

from app.core.database import Base, engine, SessionLocal
from app.core.crypto import encrypt_secret, decrypt_secret
from app.models.totp_account import TOTPAccount


def test_encryption_and_decryption():
    original_secret = "MY_TEST_SECRET_123"

    encrypted = encrypt_secret(original_secret)
    decrypted = decrypt_secret(encrypted)

    assert encrypted != original_secret
    assert decrypted == original_secret


def test_totp_secret_is_saved_encrypted():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    username = "db_test_" + uuid.uuid4().hex[:8]
    original_secret = "MY_TEST_SECRET_123"

    try:
        encrypted = encrypt_secret(original_secret)

        account = TOTPAccount(
            username=username,
            secret_encrypted=encrypted,
            enabled=False
        )

        db.add(account)
        db.commit()

        saved_account = db.query(TOTPAccount).filter_by(
            username=username
        ).first()

        assert saved_account is not None
        assert saved_account.secret_encrypted != original_secret

        recovered_secret = decrypt_secret(
            saved_account.secret_encrypted
        )

        assert recovered_secret == original_secret

    finally:
        db.query(TOTPAccount).filter_by(
            username=username
        ).delete()
        db.commit()
        db.close()
