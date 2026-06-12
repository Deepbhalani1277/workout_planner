"""
User / Profile Pydantic schemas — serialisation shapes
for user and profile data going in and out of the API.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class ProfileUpdate(BaseModel):
    age: int | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    fitness_level: str | None = None
    fitness_goal: str | None = None
    workout_frequency: int | None = None
    dietary_preference: str | None = None
    allergies: str | None = None
    calorie_target: int | None = None


class ProfileOut(ProfileUpdate):
    id: int
    user_id: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    is_google_user: bool
    created_at: datetime
    profile: ProfileOut | None = None

    model_config = {"from_attributes": True}
