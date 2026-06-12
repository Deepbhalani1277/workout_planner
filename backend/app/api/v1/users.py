"""
User endpoints.

Handles user profile retrieval and updates (height, weight,
fitness goals, dietary preferences, etc.).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_current_user():
    """Return the authenticated user's profile."""
    return {"message": "get current user — not yet implemented"}


@router.put("/me")
async def update_profile():
    """Update the authenticated user's profile fields."""
    return {"message": "update profile — not yet implemented"}
