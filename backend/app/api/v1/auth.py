"""
Authentication endpoints.

Handles user registration, login (email/password + Google OAuth),
token refresh, and logout.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register():
    """Register a new user with email and password."""
    return {"message": "register endpoint — not yet implemented"}


@router.post("/login")
async def login():
    """Authenticate with email/password and return JWT tokens."""
    return {"message": "login endpoint — not yet implemented"}


@router.post("/google")
async def google_login():
    """Authenticate via Google OAuth and return JWT tokens."""
    return {"message": "google login endpoint — not yet implemented"}


@router.post("/refresh")
async def refresh_token():
    """Exchange a valid refresh token for a new access token."""
    return {"message": "refresh endpoint — not yet implemented"}


@router.post("/logout")
async def logout():
    """Invalidate the current refresh token."""
    return {"message": "logout endpoint — not yet implemented"}
