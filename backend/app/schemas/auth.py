"""
Auth Pydantic schemas — request/response bodies for
registration, login, token management, email verification,
and password reset endpoints.

Security note: password_hash is NEVER included in any
response schema to prevent accidental credential exposure.
"""

import uuid

from pydantic import BaseModel, EmailStr


# ── User representation in token responses ────────────────────

class UserInToken(BaseModel):
    """
    Safe user payload returned alongside tokens.
    Only non-sensitive fields are exposed — no password_hash.
    """
    id: uuid.UUID
    full_name: str
    email: str
    is_onboarded: bool


# ── Register ──────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class RegisterResponse(BaseModel):
    message: str


# ── Verify Email ──────────────────────────────────────────────

class VerifyEmailRequest(BaseModel):
    token: str


class VerifyEmailResponse(BaseModel):
    message: str


# ── Login ─────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInToken


# ── Google Login ──────────────────────────────────────────────

class GoogleLoginRequest(BaseModel):
    credential: str  # Google ID token from frontend Sign-In


class GoogleLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInToken


# ── Refresh Token ─────────────────────────────────────────────

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── Logout ────────────────────────────────────────────────────

class LogoutRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    message: str


# ── Forgot Password ──────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


# ── Reset Password ────────────────────────────────────────────

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    message: str
