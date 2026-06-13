"""
Shared FastAPI dependencies.

Centralises reusable dependencies (auth, database, config) so that
routers and services can import them from one place.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.core.security import decode_token
from app.db.session import get_db

# ── OAuth2 scheme ────────────────────────────────────────────
# tokenUrl points to the login endpoint so Swagger UI's
# "Authorize" button knows where to send credentials.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

settings = get_settings()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency — extracts and validates the Bearer token
    from the Authorization header, then returns the authenticated
    User ORM object.

    Injected into any route that needs authentication:
        @router.get("/protected")
        async def protected(user = Depends(get_current_user)):
            ...

    Raises:
     • 401 if the token is missing, invalid, or the user is not found
     • 403 if the user's account has been deactivated
    """
    # Import inside function to avoid circular import
    # (models → base → models)
    from app.models.user import User

    # decode_token raises 401 if the JWT is invalid or expired
    payload = decode_token(token, settings.SECRET_KEY)

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated. Please contact support.",
        )

    return user


__all__ = ["get_db", "get_settings", "Settings", "get_current_user"]
