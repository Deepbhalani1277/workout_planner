"""
User endpoints.

Handles user profile retrieval, updates, onboarding,
and account deletion.

Thin controllers — all business logic lives in UserService.

Security:
 • Every route requires get_current_user (Bearer token).
 • user_id is ALWAYS taken from the authenticated token,
   never from the request body — prevents users from
   accessing other users' data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.user import (
    DeleteAccountResponse,
    OnboardingRequest,
    OnboardingResponse,
    OnboardingUpdateRequest,
    ProfileResponse,
    UpdateUserRequest,
    UpdateUserResponse,
    UserResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# ── Get current user ──────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return the authenticated user's info.

    user_id comes from the JWT — no one can fetch another
    user's data by guessing IDs.
    """
    return UserService.get_user(db=db, user_id=current_user.id)


# ── Update current user ──────────────────────────────────────

@router.put("/me", response_model=UpdateUserResponse)
async def update_me(
    body: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update the authenticated user's editable fields (full_name).

    Email cannot be changed through this endpoint for security
    reasons — it would require a re-verification flow.
    """
    return UserService.update_user(
        db=db,
        user_id=current_user.id,
        data=body,
    )


# ── Get profile ───────────────────────────────────────────────

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return the authenticated user's profile (onboarding data).

    Includes all fields: physical attributes, fitness goals,
    dietary preferences, and the is_complete flag.
    """
    return UserService.get_profile(db=db, user_id=current_user.id)


# ── Save onboarding ──────────────────────────────────────────

@router.post("/onboarding", response_model=OnboardingResponse)
async def save_onboarding(
    body: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Submit the initial onboarding form.

    All fields are required.  On success, is_complete is set
    to True and the frontend should redirect to the dashboard.
    """
    return UserService.save_onboarding(
        db=db,
        user_id=current_user.id,
        data=body,
    )


# ── Update onboarding ────────────────────────────────────────

@router.put("/onboarding", response_model=OnboardingResponse)
async def update_onboarding(
    body: OnboardingUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Partially update onboarding fields.

    Only the fields included in the request body are modified —
    everything else stays the same.  Useful for updating a
    single value like weight_kg after a weigh-in.
    """
    return UserService.update_onboarding(
        db=db,
        user_id=current_user.id,
        data=body,
    )


# ── Delete account ────────────────────────────────────────────

@router.delete("/me", response_model=DeleteAccountResponse)
async def delete_account(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Soft-delete the authenticated user's account.

    Sets is_active=False and revokes all refresh tokens.
    The account can be recovered within 30 days by
    contacting support.
    """
    return UserService.delete_account(db=db, user_id=current_user.id)
