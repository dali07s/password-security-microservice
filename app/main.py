from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import strength
from app.routes import generator
from app.routes import passphrase
from app.routes import totp
from app.routes import breach
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter
from app.core.database import Base, engine
from app.models.totp_account import TOTPAccount


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Password Protection and Management Microservice",
    description="""
    ## Overview

    An independent RESTful microservice providing password
    security and management functionality.

    ## Features

    - Password strength analysis using zxcvbn.
    - Cryptographically secure password generation.
    - Human-memorable passphrase generation using Diceware.
    - TOTP-based two-factor authentication.
    - Breached password analysis using Have I Been Pwned.

    ## Security

    The service uses secure random generation, encrypted TOTP
    secret storage, input validation and rate limiting.

    Do not send real passwords over unencrypted HTTP.
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Password Security",
            "description": "Password analysis and secure password generation."
        },
        {
            "name": "Passphrase Generation",
            "description": "Generation of memorable Diceware passphrases."
        },
        {
            "name": "Two-Factor Authentication",
            "description": "TOTP enrollment and code verification."
        },
        {
            "name": "Breach Detection",
            "description": "Check whether a password appears in known breach data."
        },
        {
            "name": "System",
            "description": "Microservice health and status."
        }
    ]
)

app.include_router(
    strength.router,
    prefix="/api/password",
    tags=["Password Strength"]
)

app.include_router(
    generator.router,
    prefix="/api/password",
    tags=["Password Generator"]
)
app.include_router(
    passphrase.router,
    prefix="/api/passphrase",
    tags=["Passphrase Generator"]
)

app.include_router(
    totp.router,
    prefix="/api/2fa",
    tags=["Two-Factor Authentication"]
    )

app.include_router(
    breach.router,
    prefix="/api/password",
    tags=["Password Breach Analysis"]

)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/dashboard", StaticFiles(directory="frontend", html=True), name="dashboard")

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

@app.get("/")
def home():
    return {
        "message": "Password Security Microservice is running"
    }

@app.get(
    "/health",
    tags=["System"],
    summary="Check Microservice Health",
    description="Returns the current health status of the microservice."
)
def health_check():
    return {"status": "healthy"}
    
@app.middleware("http")
async def security_headers(request, call_next):

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Referrer-Policy"] = "no-referrer"

    response.headers["Cache-Control"] = "no-store"

    return response   