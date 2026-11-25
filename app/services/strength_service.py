from zxcvbn import zxcvbn


def analyze_password(password: str):

    if not password:
        return {
            "length": 0,
            "diversity": 0,
            "score": 0,
            "strength": "Very Weak",
            "estimated_guesses": 0,
            "feedback": {
                "warning": "Password cannot be empty",
                "suggestions": ["Use a longer password"]
            }
        }

    # Analyze the password using zxcvbn
    result = zxcvbn(password)

    # Calculate basic character diversity
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() and not c.isspace() for c in password)

    diversity = sum([
        has_upper,
        has_lower,
        has_digit,
        has_symbol
    ])

    # Convert the score into a readable label
    levels = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Strong"
    }

    return {
        "length": len(password),
        "diversity": diversity,
        "score": result["score"],
        "strength": levels[result["score"]],
        "estimated_guesses": result["guesses"],
        "feedback": result["feedback"]
    }