import sys
from pathlib import Path

# Ensure project root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.crypto import encrypt_secret, decrypt_secret

secret = "MY_TEST_TOTP_SECRET_123"

encrypted = encrypt_secret(secret)
decrypted = decrypt_secret(encrypted)

print("Original:", secret)
print("Encrypted:", encrypted)
print("Decrypted:", decrypted)

assert secret == decrypted

print("Encryption test passed!")