import secrets
import string


def generate_password(length: int):

    # Define character categories
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+"

    # Combine all allowed characters
    all_characters = lowercase + uppercase + digits + symbols

    # Guarantee at least one character from each category
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]

    # Fill the remaining positions
    for _ in range(length - 4):
        password.append(secrets.choice(all_characters))

    # Securely shuffle the characters
    secrets.SystemRandom().shuffle(password)

    return "".join(password)