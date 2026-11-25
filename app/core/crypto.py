
import os
from pathlib import Path
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Explicitly locate and load .env from the project root
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)
load_dotenv()

key = os.getenv("TOTP_ENCRYPTION_KEY")

if not key:
    raise RuntimeError("TOTP_ENCRYPTION_KEY is missing")

key = key.strip()
if len(key) == 43 and not key.endswith("="):
    key += "="

fernet = Fernet(key.encode())


def encrypt_secret(secret: str) -> str:
    encrypted = fernet.encrypt(secret.encode())
    return encrypted.decode()


def decrypt_secret(encrypted_secret: str) -> str:
    decrypted = fernet.decrypt(encrypted_secret.encode())
    return decrypted.decode()
