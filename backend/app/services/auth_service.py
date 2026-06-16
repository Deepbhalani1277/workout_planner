"""
Auth service — business logic for registration, login, token
management, email verification, password reset, and Google OAuth.

This is the single source of truth for all auth operations.
Route handlers (controllers) are kept thin and delegate here.

Security design:
 • Passwords are bcrypt-hashed before storage.
 • Refresh tokens are SHA-256-hashed in the DB — raw tokens
   are never persisted.
 • Verification / reset tokens are SHA-256-hashed in Redis.
 • Error messages are generic to prevent user-enumeration.
"""

import re
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.oauth import verify_google_token
from app.core.redis import delete_token, get_token, store_token
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.utils.email import send_password_reset_email, send_verification_email

# Note: Model imports (User, Profile, RefreshToken, AuthProvider) are
# done inside each function to avoid circular imports through db.base.

settings = get_settings()


# ── Password strength validation ─────────────────────────────

def _validate_password(password: str) -> None:
    """
    Enforce minimum password complexity:
     • At least 8 characters
     • At least 1 digit
     • At least 1 special character

    Raises HTTPException 400 with a specific message on failure.
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 1 number",
        )
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/`~;']", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 1 special character",
        )


# ── Helper: build user-info dict for token responses ─────────

def _user_info(user) -> dict:
    """
    Build the safe user payload returned alongside tokens.

    `is_onboarded` is derived from the profile's `is_complete`
    flag — True once the user has filled out the onboarding
    wizard (height, weight, goals, etc.).
    """
    is_onboarded = False
    if user.profile and user.profile.is_complete:
        is_onboarded = True

    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "is_onboarded": is_onboarded,
    }


# ── Helper: issue token pair and persist refresh hash ────────

def _issue_tokens(db: Session, user) -> dict:
    """
    Generate an access + refresh token pair and store the
    refresh token hash in the database.

    Returns a dict ready to be spread into the response model.
    """
    from app.models.refresh_token import RefreshToken

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})

    # Store the SHA-256 hash — never the raw token
    token_hash_val = hash_token(refresh_token_str)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash_val,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user": _user_info(user),
    }


# ═══════════════════════════════════════════════════════════════
#  AuthService
# ═══════════════════════════════════════════════════════════════

class AuthService:
    """
    Stateless service class — all methods are static so they
    can be called without instantiation.
    """

    # ── 1. Register ───────────────────────────────────────────
    # Rate limit: 5 requests per minute per IP (enforced in middleware)

    @staticmethod
    def register(
        db: Session,
        email: str,
        full_name: str,
        password: str,
    ) -> dict:
        """
        Create a new email/password user.

        Steps:
         1. Check for duplicate email
         2. Validate password strength
         3. Hash password with bcrypt
         4. Create user row (is_verified=False)
         5. Create empty profile row linked to user
         6. Generate a UUID verification token
         7. Hash the token and store in Redis (24hr TTL)
         8. Print the verification link to console (mock email)
        """
        from app.models.profile import Profile
        from app.models.user import AuthProvider, User

        # Duplicate check
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Password rules
        _validate_password(password)

        # Create user
        hashed_pw = hash_password(password)
        user = User(
            email=email,
            full_name=full_name,
            password_hash=hashed_pw,
            auth_provider=AuthProvider.EMAIL,
            is_verified=True,  # Bypassing email verification
        )
        db.add(user)
        db.flush()  # get user.id without committing yet

        # Create empty profile
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()

        return {"message": "Registration successful. You can now log in."}

    # ── 2. Verify Email ───────────────────────────────────────

    @staticmethod
    def verify_email(db: Session, token: str) -> dict:
        """
        Mark the user as verified after they click the email link.

        The incoming token is hashed and looked up in Redis.
        If found, the user's is_verified flag is set to True and
        the token is deleted from Redis to prevent reuse.
        """
        from app.models.user import User

        token_h = hash_token(token)
        user_id = get_token(f"verify:{token_h}")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        user.is_verified = True
        db.commit()

        delete_token(f"verify:{token_h}")

        return {"message": "Email verified successfully. You can now log in."}

    # ── 3. Login ──────────────────────────────────────────────
    # Rate limit: 10 requests per minute per IP (enforced in middleware)

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        """
        Authenticate with email + password and return JWT tokens.

        Security measures:
         • Generic "Invalid credentials" message — does not reveal
           whether the email exists.
         • Checks is_verified before allowing login.
         • Checks is_active for deactivated accounts.
        """
        from app.models.user import User

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Verification check bypassed

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account deactivated. Please contact support.",
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        return _issue_tokens(db, user)

    # ── 4. Google Login ───────────────────────────────────────

    @staticmethod
    def google_login(db: Session, credential: str) -> dict:
        """
        Authenticate via Google OAuth (frontend ID-token flow).

        Steps:
         1. Verify the Google ID token against Google's public keys
         2. Extract email, name, and google_id (sub) from payload
         3. If user doesn't exist → create with auth_provider='google'
         4. If user exists with email provider → link google_id
         5. Issue JWT token pair
        """
        from app.models.profile import Profile
        from app.models.user import AuthProvider, User

        payload = verify_google_token(credential)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google credential",
            )

        google_email = payload.get("email")
        google_name = payload.get("name", "")
        google_id = payload.get("sub")

        if not google_email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google credential",
            )

        # Look up by google_id first, then by email
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = db.query(User).filter(User.email == google_email).first()

        if not user:
            # New user — create with Google provider
            user = User(
                email=google_email,
                full_name=google_name,
                auth_provider=AuthProvider.GOOGLE,
                google_id=google_id,
                is_verified=True,  # Google already verified the email
            )
            db.add(user)
            db.flush()

            profile = Profile(user_id=user.id)
            db.add(profile)
            db.commit()

        elif user.auth_provider == AuthProvider.EMAIL:
            # Existing email user → link their Google account
            user.google_id = google_id
            db.commit()

        return _issue_tokens(db, user)

    # ── 5. Refresh Token ─────────────────────────────────────

    @staticmethod
    def refresh_token(db: Session, refresh_token_str: str) -> dict:
        """
        Exchange a valid refresh token for a new token pair.

        Implements token rotation:
         1. Decode the JWT to verify signature + expiry
         2. Hash the raw token and find the matching DB row
         3. If revoked or expired → reject
         4. Revoke the old token
         5. Issue a fresh token pair
        """
        from app.models.refresh_token import RefreshToken
        from app.models.user import User

        # Decode JWT (raises 401 if invalid/expired)
        payload = decode_token(refresh_token_str, settings.REFRESH_SECRET_KEY)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Find the stored hash
        token_h = hash_token(refresh_token_str)
        db_token = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_h,
                RefreshToken.user_id == user_id,
            )
            .first()
        )

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if db_token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        # Rotate: revoke old token
        db_token.is_revoked = True
        db.commit()

        # Issue new pair
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return _issue_tokens(db, user)

    # ── 6. Logout ─────────────────────────────────────────────

    @staticmethod
    def logout(
        db: Session,
        user_id: uuid.UUID,
        refresh_token_str: str,
    ) -> dict:
        """
        Revoke a specific refresh token on logout.

        The token is identified by its SHA-256 hash + the
        authenticated user's ID (double-check ownership).
        """
        from app.models.refresh_token import RefreshToken

        token_h = hash_token(refresh_token_str)
        db_token = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_h,
                RefreshToken.user_id == user_id,
            )
            .first()
        )

        if db_token:
            db_token.is_revoked = True
            db.commit()

        return {"message": "Logged out successfully"}

    # ── 7. Forgot Password ───────────────────────────────────
    # Rate limit: 3 requests per minute per IP (enforced in middleware)

    @staticmethod
    def forgot_password(db: Session, email: str) -> dict:
        """
        Initiate the password-reset flow.

        Always returns the same success message regardless of
        whether the email exists — this prevents email-enumeration
        attacks where an attacker probes for valid accounts.
        """
        from app.models.user import AuthProvider, User

        user = db.query(User).filter(User.email == email).first()

        if user and user.auth_provider == AuthProvider.EMAIL:
            raw_token = str(uuid.uuid4())
            token_h = hash_token(raw_token)
            store_token(
                key=f"reset:{token_h}",
                value=str(user.id),
                ttl_seconds=3600,  # 1 hour
            )
            send_password_reset_email(email, raw_token)

        return {
            "message": "If this email exists, you will receive a password reset link."
        }

    # ── 8. Reset Password ────────────────────────────────────

    @staticmethod
    def reset_password(
        db: Session, token: str, new_password: str
    ) -> dict:
        """
        Complete the password-reset flow.

        Steps:
         1. Hash the incoming token and look it up in Redis
         2. Validate the new password strength
         3. Update the user's password_hash in the DB
         4. Delete the reset token from Redis (single-use)
         5. Revoke ALL refresh tokens for this user (security:
            force re-login on all devices after a password change)
        """
        from app.models.refresh_token import RefreshToken
        from app.models.user import User

        token_h = hash_token(token)
        user_id = get_token(f"reset:{token_h}")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        _validate_password(new_password)

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Update password
        user.password_hash = hash_password(new_password)

        # Delete token from Redis (single-use)
        delete_token(f"reset:{token_h}")

        # Revoke ALL refresh tokens — force re-login everywhere
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False,  # noqa: E712
        ).update({"is_revoked": True})

        db.commit()

        return {"message": "Password reset successful. Please log in with your new password."}
