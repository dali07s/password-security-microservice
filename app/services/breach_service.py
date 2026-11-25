import hashlib
import requests


HIBP_API_URL = "https://api.pwnedpasswords.com/range/"


def check_password_breach(password: str):

    # Step 1: Calculate the SHA-1 hash locally
    sha1_hash = hashlib.sha1(
        password.encode("utf-8")
    ).hexdigest().upper()

    # Step 2: Split the hash into prefix and suffix
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    # Step 3: Send only the prefix to HIBP
    response = requests.get(
        HIBP_API_URL + prefix,
        headers={
            "User-Agent": "Password-Security-Microservice/1.0",
            "Add-Padding": "true"
        },
        timeout=10
    )

    response.raise_for_status()

    # Step 4: Compare the returned suffixes locally
    for line in response.text.splitlines():

        hash_suffix, count = line.split(":")

        if hash_suffix.upper() == suffix:
            return {
                "is_breached": True,
                "times_seen": int(count)
            }

    # Password was not found
    return {
        "is_breached": False,
        "times_seen": 0
    }