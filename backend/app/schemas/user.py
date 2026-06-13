"""
User / Profile Pydantic schemas — serialisation shapes
for user and profile data going in and out of the API.

Security note: password_hash is NEVER included in any
response schema.  UserResponse only exposes safe fields.
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


# ═══════════════════════════════════════════════════════════════
#  Enums (mirror the SQLAlchemy enums in models/profile.py)
# ═══════════════════════════════════════════════════════════════

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class FitnessGoalEnum(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTAIN = "maintain"
    STAMINA = "stamina"


class ActivityLevelEnum(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    VERY_ACTIVE = "very_active"


class DietTypeEnum(str, Enum):
    VEGETARIAN = "vegetarian"
    NON_VEGETARIAN = "non_vegetarian"
    VEGAN = "vegan"
    EGGETARIAN = "eggetarian"


class BudgetRangeEnum(str, Enum):
    BELOW_3000 = "below_3000"
    RANGE_3000_6000 = "3000_6000"
    ABOVE_6000 = "above_6000"


# ═══════════════════════════════════════════════════════════════
#  User schemas
# ═══════════════════════════════════════════════════════════════

class UserResponse(BaseModel):
    """
    Safe user representation — never exposes password_hash.
    Returned by GET /users/me.
    """
    id: uuid.UUID
    full_name: str
    email: EmailStr
    auth_provider: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    """
    Only full_name can be updated.
    Email changes are not allowed for security reasons
    (would require re-verification flow).
    """
    full_name: str = Field(..., min_length=1, max_length=100)


class UpdateUserResponse(BaseModel):
    message: str
    full_name: str


# ═══════════════════════════════════════════════════════════════
#  Profile schemas
# ═══════════════════════════════════════════════════════════════

class ProfileResponse(BaseModel):
    """
    Full profile representation returned by GET /users/profile.
    Includes all onboarding fields + metadata.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    age: int | None = None
    gender: GenderEnum | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    fitness_goal: FitnessGoalEnum | None = None
    activity_level: ActivityLevelEnum | None = None
    equipment: list[str] | None = None
    diet_type: DietTypeEnum | None = None
    allergies: str | None = None
    budget_range: BudgetRangeEnum | None = None
    is_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Onboarding (initial submission — all fields required) ─────

class OnboardingRequest(BaseModel):
    """
    All onboarding fields are required on first submission.

    Validations enforce realistic ranges:
     • age 13–80: minors under 13 need parental consent,
       80+ is a safety concern for AI-generated plans.
     • height 100–250 cm: covers the realistic human range.
     • weight 30–300 kg: same rationale.
    """
    age: int = Field(..., ge=13, le=80)
    gender: GenderEnum
    height_cm: float = Field(..., ge=100, le=250)
    weight_kg: float = Field(..., ge=30, le=300)
    fitness_goal: FitnessGoalEnum
    activity_level: ActivityLevelEnum
    equipment: list[str] = Field(..., min_length=0)
    diet_type: DietTypeEnum
    allergies: str | None = None
    budget_range: BudgetRangeEnum


class OnboardingResponse(BaseModel):
    message: str
    is_complete: bool


# ── Onboarding update (partial — all fields optional) ─────────

class OnboardingUpdateRequest(BaseModel):
    """
    Partial update — only provided fields are written.
    This lets the user tweak one field (e.g. weight_kg after
    a weigh-in) without re-submitting the entire form.

    Same validations as OnboardingRequest but all fields
    are optional.
    """
    age: int | None = Field(None, ge=13, le=80)
    gender: GenderEnum | None = None
    height_cm: float | None = Field(None, ge=100, le=250)
    weight_kg: float | None = Field(None, ge=30, le=300)
    fitness_goal: FitnessGoalEnum | None = None
    activity_level: ActivityLevelEnum | None = None
    equipment: list[str] | None = None
    diet_type: DietTypeEnum | None = None
    allergies: str | None = None
    budget_range: BudgetRangeEnum | None = None


# ── Delete account ────────────────────────────────────────────

class DeleteAccountResponse(BaseModel):
    message: str
