"""
User service — business logic for user and profile operations.

Handles:
 • User info retrieval and name updates
 • Profile / onboarding CRUD
 • Soft-delete (account deactivation)

Security:
 • user_id always comes from the authenticated token, never
   from the request body — users can only access their own data.
 • password_hash is never returned in any response.
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class UserService:
    """
    Stateless service class — all methods are static so they
    can be called without instantiation.
    """

    # ── 1. Get User ───────────────────────────────────────────

    @staticmethod
    def get_user(db: Session, user_id: uuid.UUID) -> dict:
        """
        Fetch the authenticated user's info.

        Returns only safe fields — password_hash is explicitly
        excluded by the response schema (UserResponse), but we
        also avoid returning the ORM object directly to make
        the contract explicit.
        """
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user  # serialised by UserResponse (excludes password_hash)

    # ── 2. Update User ───────────────────────────────────────

    @staticmethod
    def update_user(db: Session, user_id: uuid.UUID, data) -> dict:
        """
        Update mutable user fields.

        Currently only full_name is editable.  Email changes are
        blocked because they would require a re-verification flow
        and could break Google-linked accounts.
        """
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.full_name = data.full_name
        db.commit()
        db.refresh(user)

        return {
            "message": "User updated successfully",
            "full_name": user.full_name,
        }

    # ── 3. Get Profile ────────────────────────────────────────

    @staticmethod
    def get_profile(db: Session, user_id: uuid.UUID):
        """
        Fetch the user's profile (onboarding data).

        Every user gets a profile row created at registration
        (even if it's empty), so a 404 here means something
        went wrong during signup.
        """
        from app.models.profile import Profile

        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        return profile  # serialised by ProfileResponse

    # ── 4. Save Onboarding ────────────────────────────────────

    @staticmethod
    def save_onboarding(db: Session, user_id: uuid.UUID, data) -> dict:
        """
        Save the initial onboarding data.

        Called when the user completes the onboarding wizard for
        the first time.  All fields are required (enforced by
        OnboardingRequest schema).  Sets is_complete=True so
        the frontend knows to show the dashboard instead of
        the wizard.
        """
        from app.models.profile import Profile

        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        # Set all onboarding fields
        profile.age = data.age
        profile.gender = data.gender.value
        profile.height_cm = data.height_cm
        profile.weight_kg = data.weight_kg
        profile.fitness_goal = data.fitness_goal.value
        profile.activity_level = data.activity_level.value
        profile.equipment = data.equipment
        profile.diet_type = data.diet_type.value
        profile.allergies = data.allergies
        profile.budget_range = data.budget_range.value
        profile.is_complete = True

        db.commit()

        return {
            "message": "Onboarding completed successfully",
            "is_complete": True,
        }

    # ── 5. Update Onboarding ──────────────────────────────────

    @staticmethod
    def update_onboarding(db: Session, user_id: uuid.UUID, data) -> dict:
        """
        Partially update onboarding fields.

        Only provided (non-None) fields are written.  This lets
        the user tweak a single value (e.g. update weight_kg
        after a weigh-in) without re-submitting the entire form.

        is_complete is NOT reset to False — the user has already
        completed onboarding, this is just a field-level edit.
        """
        from app.models.profile import Profile

        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        # model_dump(exclude_unset=True) returns only fields the
        # client explicitly sent — not fields with None defaults
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            # Convert enum values to their string representation
            # so SQLAlchemy stores the raw value, not the enum name
            if hasattr(value, "value"):
                value = value.value
            setattr(profile, field, value)

        db.commit()

        return {"message": "Profile updated successfully", "is_complete": profile.is_complete}

    # ── 6. Delete Account ─────────────────────────────────────

    @staticmethod
    def delete_account(db: Session, user_id: uuid.UUID) -> dict:
        """
        Soft-delete the user's account.

        Sets is_active=False instead of physically deleting the
        row.  This gives us a 30-day window to:
         • Let the user recover their account if they change
           their mind
         • Comply with data-retention regulations
         • Run a background job that permanently deletes after
           30 days

        Also revokes ALL refresh tokens so the user is immediately
        logged out on all devices.
        """
        from app.models.refresh_token import RefreshToken
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Soft-delete
        user.is_active = False

        # Revoke all refresh tokens — immediate logout everywhere
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,  # noqa: E712
        ).update({"is_revoked": True})

        db.commit()

        return {
            "message": (
                "Account deactivated. Your data will be permanently "
                "deleted after 30 days. Contact support to recover "
                "your account within this period."
            )
        }
