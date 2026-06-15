"""
Diet Pydantic schemas — request/response bodies for
diet plan generation, retrieval, meal swapping, and deletion.

These schemas validate the JSON structure that Gemini returns
and define the shape of API responses.

Security note: No sensitive user data is exposed in these
schemas — they only contain plan content.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Meal ──────────────────────────────────────────────────────

class MealSchema(BaseModel):
    """
    A single meal within a diet plan day.

    Fields:
     • name:       meal name (e.g. "Poha with peanuts")
     • calories:   calorie count for the meal
     • protein_g:  protein in grams
     • carbs_g:    carbohydrates in grams
     • fat_g:      fat in grams
     • prep_note:  preparation tip or cooking note
    """
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    prep_note: str


# ── Day Meals ─────────────────────────────────────────────────

class DayMealsSchema(BaseModel):
    """
    The 5 meal slots for a single day.

    Each slot maps to a MealSchema object.
    """
    breakfast: MealSchema
    lunch: MealSchema
    dinner: MealSchema
    snack_1: MealSchema
    snack_2: MealSchema


# ── Diet Day ──────────────────────────────────────────────────

class DietDaySchema(BaseModel):
    """
    One day within the 7-day diet plan.

    Contains the day name, total calorie target, and all meals.
    """
    day: str
    total_calories: int
    meals: DayMealsSchema


# ── Full Plan Data ────────────────────────────────────────────

class DietPlanDataSchema(BaseModel):
    """
    The top-level structure returned by Gemini.
    Must contain exactly 7 days (Monday–Sunday).
    """
    week: list[DietDaySchema] = Field(..., min_length=7, max_length=7)


# ── API Responses ─────────────────────────────────────────────

class DietPlanResponse(BaseModel):
    """
    Response body for POST /diet/generate and GET /diet/me.

    plan_id and generated_at come from the DB row; plan is the
    validated Gemini output.
    """
    plan_id: uuid.UUID
    generated_at: datetime
    plan: DietPlanDataSchema


# ── Swap Meal ─────────────────────────────────────────────────

class SwapMealRequest(BaseModel):
    """
    Request body for POST /diet/swap-meal.

    day: one of Monday–Sunday
    meal_slot: one of breakfast, lunch, dinner, snack_1, snack_2
    """
    day: str
    meal_slot: str


class SwapMealResponse(BaseModel):
    """
    Response body for POST /diet/swap-meal.

    Returns the day, meal_slot, and the newly generated meal.
    """
    day: str
    meal_slot: str
    meal: MealSchema


# ── Delete ────────────────────────────────────────────────────

class DeleteDietResponse(BaseModel):
    """Response body for DELETE /diet/me."""
    message: str
