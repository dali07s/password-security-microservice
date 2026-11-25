
# Password Protection and Management Microservice
## REST API Documentation

Version: 1.0.0

### Base URL

http://127.0.0.1:8000

### 1. Password Strength Analysis

- Method: POST
- Endpoint: /api/password/strength
- Purpose: Analyzes password strength using zxcvbn.

Request:
{
  "password": "MyPassword123!"
}

Successful response (200):
{
  "length": 14,
  "diversity": 4,
  "score": 3,
  "strength": "Good",
  "estimated_guesses": 1000000000,
  "feedback": {}
}

Possible errors:
- 422: Invalid request body.

### 2. Secure Password Generation

- Method: POST
- Endpoint: /api/password/generate
- Purpose: Generates a secure random password using Python secrets.

Request:
{
  "length": 16
}

Successful response (200):
{
  "password": "<generated-password>",
  "length": 16
}

Possible errors:
- 422: Length outside the allowed range (4–128).

### 3. Memorable Passphrase Generation

- Method: POST
- Endpoint: /api/passphrase/generate
- Purpose: Generates a passphrase using the EFF Diceware wordlist.

Request:
{
  "number_of_words": 5
}

Successful response (200):
{
  "passphrase": "<generated-passphrase>",
  "number_of_words": 5
}

Possible errors:
- 422: Word count outside the allowed range (4–10).

### 4. TOTP Setup

- Method: POST
- Endpoint: /api/2fa/setup
- Purpose: Creates a TOTP enrollment and stores the encrypted secret.

Request:
{
  "username": "student01"
}

Successful response (200):
{
  "username": "student01",
  "qr_code_base64": "<base64-encoded-png>",
  "message": "Scan the QR code with your authenticator app"
}

Possible errors:
- 409: TOTP already registered.
- 422: Invalid username.

### 5. TOTP Verification

- Method: POST
- Endpoint: /api/2fa/verify
- Purpose: Verifies a six-digit TOTP code.

Request:
{
  "username": "student01",
  "code": "123456"
}

Successful response (200):
{
  "verified": true,
  "message": "Authentication successful"
}

Possible errors:
- 404: TOTP account not found.
- 422: Invalid request or code format.
- 429: Rate limit exceeded.

### 6. Breached Password Analysis

- Method: POST
- Endpoint: /api/password/breach-check
- Purpose: Checks a password against the HIBP Pwned Passwords database.

Request:
{
  "password": "MyPassword123!"
}

Successful response (200), if found:
{
  "is_breached": true,
  "times_seen": 25
}

Successful response (200), if not found:
{
  "is_breached": false,
  "times_seen": 0
}

Possible errors:
- 422: Invalid request body.
- 429: Rate limit exceeded.
- 503: External service unavailable.

### 7. Health Check

- Method: GET
- Endpoint: /health
- Purpose: Checks whether the API is running.

Successful response (200):
{
  "status": "healthy"
}

## Security Notes

- Secure password generation uses Python's secrets module.
- Password strength analysis uses zxcvbn locally.
- TOTP secrets are encrypted before database storage.
- Breach checking uses the HIBP k-anonymity mechanism.
- Sensitive API traffic should use HTTPS in production.
- Rate limiting protects selected sensitive endpoints.
- Passwords and TOTP secrets must not be written to application logs.
