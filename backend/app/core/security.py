"""
Security utilities — JWT creation / verification and
password hashing.

All secrets come from config.py (loaded from .env) — nothing
is hardcoded here.

Functions:
 • hash_password / verify_password — bcrypt wrappers
 • create_access_token / create_refresh_token — JWT generators
 • decode_token — unified JWT decoder that raises 401 on failure
 • hash_token — SHA-256 hash for storing tokens in DB/Redis
"""

import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# ── Password hashing ─────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ── JWT tokens ────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Create a short-lived access token.

    Embeds the supplied data (typically {"sub": user_id}) plus an
    expiry timestamp and a type="access" claim so refresh tokens
    cannot be used in place of access tokens.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived refresh token.

    Same structure as an access token but with a longer expiry
    and type="refresh" to prevent cross-use.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm="HS256")


def decode_token(token: str, secret_key: str) -> dict:
    """
    Decode and validate a JWT token.

    Raises HTTPException 401 if the token is invalid, expired,
    or tampered with.  Returns the full payload dict on success.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Token hashing (SHA-256) ──────────────────────────────────

def hash_token(token: str) -> str:
    """
    Return the SHA-256 hex digest of a token string.

    Used to store refresh tokens and password-reset tokens
    securely in the database / Redis.  Even if the store is
    compromised, the raw tokens cannot be recovered.
    """
    return hashlib.sha256(token.encode()).hexdigest()
