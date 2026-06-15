"""
Diet endpoint tests.

Covers:
 • Generate plan success (mocked Gemini)
 • Get active plan success
 • Swap meal success (mocked Gemini)
 • Swap meal with invalid slot → 400
 • Delete plan success

All Gemini API calls are mocked — no real AI calls are made.
"""

import pytest
from unittest.mock import patch

from tests.conftest import (
    create_onboarded_user,
    get_auth_header,
)


# ── Sample data returned by "Gemini" ─────────────────────────

MOCK_MEAL = {
    "name": "Poha with peanuts",
    "calories": 350,
    "protein_g": 10,
    "carbs_g": 58,
    "fat_g": 8,
    "prep_note": "Add lemon juice at end",
}

MOCK_DIET_PLAN = {
    "week": [
        {
            "day": day,
            "total_calories": 2200,
            "meals": {
                "breakfast": {
                    "name": "Poha with peanuts",
                    "calories": 350,
                    "protein_g": 10,
                    "carbs_g": 58,
                    "fat_g": 8,
                    "prep_note": "Add lemon juice at end",
                },
                "lunch": {
                    "name": "Dal Rice",
                    "calories": 500,
                    "protein_g": 18,
                    "carbs_g": 70,
                    "fat_g": 12,
                    "prep_note": "Use brown rice",
                },
                "dinner": {
                    "name": "Paneer Tikka with Roti",
                    "calories": 550,
                    "protein_g": 25,
                    "carbs_g": 45,
                    "fat_g": 20,
                    "prep_note": "Grill the paneer",
                },
                "snack_1": {
                    "name": "Mixed Nuts",
                    "calories": 200,
                    "protein_g": 6,
                    "carbs_g": 10,
                    "fat_g": 16,
                    "prep_note": "Unsalted almonds + walnuts",
                },
                "snack_2": {
                    "name": "Fruit Chaat",
                    "calories": 150,
                    "protein_g": 2,
                    "carbs_g": 35,
                    "fat_g": 1,
                    "prep_note": "Season with chaat masala",
                },
            },
        }
        for day in [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday",
        ]
    ]
}

MOCK_SWAP_MEAL = {
    "name": "Idli Sambar",
    "calories": 300,
    "protein_g": 8,
    "carbs_g": 55,
    "fat_g": 5,
    "prep_note": "Serve with coconut chutney",
}


class TestGenerateDiet:
    """Tests for POST /api/v1/diet/generate"""

    @patch("app.services.ai_service.AIService.generate_diet_plan")
    def test_generate_plan_success(self, mock_gen, client, db_session):
        """Generating a diet plan with a complete profile succeeds."""
        mock_gen.return_value = MOCK_DIET_PLAN

        user = create_onboarded_user(db_session, email="diet@example.com")
        headers = get_auth_header(user)

        response = client.post("/api/v1/diet/generate", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "plan_id" in data
        assert "generated_at" in data
        assert len(data["plan"]["week"]) == 7
        assert data["plan"]["week"][0]["meals"]["breakfast"]["name"] == "Poha with peanuts"


class TestGetDiet:
    """Tests for GET /api/v1/diet/me"""

    @patch("app.services.ai_service.AIService.generate_diet_plan")
    def test_get_active_plan_success(self, mock_gen, client, db_session):
        """Getting the active diet plan returns it after generation."""
        mock_gen.return_value = MOCK_DIET_PLAN

        user = create_onboarded_user(db_session, email="getdiet@example.com")
        headers = get_auth_header(user)

        # Generate first
        client.post("/api/v1/diet/generate", headers=headers)

        # Then retrieve
        response = client.get("/api/v1/diet/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "plan_id" in data
        assert len(data["plan"]["week"]) == 7


class TestSwapMeal:
    """Tests for POST /api/v1/diet/swap-meal"""

    @patch("app.services.ai_service.AIService.swap_meal")
    @patch("app.services.ai_service.AIService.generate_diet_plan")
    def test_swap_meal_success(self, mock_gen, mock_swap, client, db_session):
        """Swapping a valid meal slot returns the new meal."""
        mock_gen.return_value = MOCK_DIET_PLAN
        mock_swap.return_value = MOCK_SWAP_MEAL

        user = create_onboarded_user(db_session, email="swap@example.com")
        headers = get_auth_header(user)

        # Generate first
        client.post("/api/v1/diet/generate", headers=headers)

        # Swap breakfast on Monday
        response = client.post(
            "/api/v1/diet/swap-meal",
            headers=headers,
            json={"day": "Monday", "meal_slot": "breakfast"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["day"] == "Monday"
        assert data["meal_slot"] == "breakfast"
        assert data["meal"]["name"] == "Idli Sambar"

    @patch("app.services.ai_service.AIService.generate_diet_plan")
    def test_swap_meal_invalid_slot(self, mock_gen, client, db_session):
        """Swapping with an invalid meal_slot returns 400."""
        mock_gen.return_value = MOCK_DIET_PLAN

        user = create_onboarded_user(db_session, email="invalid@example.com")
        headers = get_auth_header(user)

        # Generate first
        client.post("/api/v1/diet/generate", headers=headers)

        # Try invalid slot
        response = client.post(
            "/api/v1/diet/swap-meal",
            headers=headers,
            json={"day": "Monday", "meal_slot": "midnight_snack"},
        )
        assert response.status_code == 400
        assert "Invalid meal_slot" in response.json()["detail"]


class TestDeleteDiet:
    """Tests for DELETE /api/v1/diet/me"""

    @patch("app.services.ai_service.AIService.generate_diet_plan")
    def test_delete_plan_success(self, mock_gen, client, db_session):
        """Deleting the active diet plan sets is_active=False."""
        mock_gen.return_value = MOCK_DIET_PLAN

        user = create_onboarded_user(db_session, email="deldiet@example.com")
        headers = get_auth_header(user)

        # Generate first
        client.post("/api/v1/diet/generate", headers=headers)

        # Delete
        response = client.delete("/api/v1/diet/me", headers=headers)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

        # Verify it's gone
        get_response = client.get("/api/v1/diet/me", headers=headers)
        assert get_response.status_code == 404
