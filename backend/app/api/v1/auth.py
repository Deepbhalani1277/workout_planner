"""
Authentication endpoints.

Thin controllers — all business logic lives in AuthService.
Each handler parses the request body, delegates to the service,
and returns the response.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    GoogleLoginRequest,
    GoogleLoginResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Register ──────────────────────────────────────────────────
# Rate limit: 5 requests per minute per IP (enforced in middleware)

@router.post("/register", response_model=RegisterResponse)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email and password."""
    return AuthService.register(
        db=db,
        email=body.email,
        full_name=body.full_name,
        password=body.password,
    )


# ── Verify Email ─────────────────────────────────────────────

@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(body: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify a user's email address using the token from the verification link."""
    return AuthService.verify_email(db=db, token=body.token)


# ── Login ─────────────────────────────────────────────────────
# Rate limit: 10 requests per minute per IP (enforced in middleware)

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email/password and return JWT tokens."""
    return AuthService.login(
        db=db,
        email=body.email,
        password=body.password,
    )


# ── Google Login ──────────────────────────────────────────────

@router.post("/google", response_model=GoogleLoginResponse)
async def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Authenticate via Google OAuth and return JWT tokens."""
    return AuthService.google_login(db=db, credential=body.credential)


# ── Refresh Token ─────────────────────────────────────────────

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new token pair."""
    return AuthService.refresh_token(
        db=db,
        refresh_token_str=body.refresh_token,
    )


# ── Logout (protected) ───────────────────────────────────────

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    body: LogoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Invalidate the provided refresh token.

    Requires a valid access token in the Authorization header
    so we know which user is logging out.
    """
    return AuthService.logout(
        db=db,
        user_id=current_user.id,
        refresh_token_str=body.refresh_token,
    )


# ── Forgot Password ──────────────────────────────────────────
# Rate limit: 3 requests per minute per IP (enforced in middleware)

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send a password-reset link to the user's email (if it exists)."""
    return AuthService.forgot_password(db=db, email=body.email)


# ── Reset Password ────────────────────────────────────────────

@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset the user's password using the token from the reset link."""
    return AuthService.reset_password(
        db=db,
        token=body.token,
        new_password=body.new_password,
    )
