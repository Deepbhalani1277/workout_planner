"""
Workout endpoint tests.

Covers:
 • Generate plan without onboarding → 400
 • Generate plan success (mocked Gemini)
 • Get active plan success
 • Get active plan when none exists → 404
 • Delete plan success

All Gemini API calls are mocked — no real AI calls are made.
"""

import pytest
from unittest.mock import patch

from tests.conftest import (
    create_onboarded_user,
    create_test_user,
    get_auth_header,
)


# ── Sample plan data returned by "Gemini" ────────────────────

MOCK_WORKOUT_PLAN = {
    "week": [
        {
            "day": day,
            "focus": "Rest" if day == "Sunday" else "Full Body",
            "is_rest_day": day == "Sunday",
            "exercises": [] if day == "Sunday" else [
                {
                    "name": "Push-ups",
                    "sets": 3,
                    "reps": "12-15",
                    "rest_seconds": 60,
                    "tip": "Keep core tight",
                }
            ],
        }
        for day in [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday",
        ]
    ]
}


class TestGenerateWorkout:
    """Tests for POST /api/v1/workout/generate"""

    def test_generate_plan_without_onboarding(self, client, db_session):
        """Generating a plan without completing onboarding → 400."""
        user = create_test_user(db_session, email="noonboard@example.com")
        headers = get_auth_header(user)

        response = client.post("/api/v1/workout/generate", headers=headers)
        assert response.status_code == 400
        assert "complete your profile" in response.json()["detail"]

    @patch("app.services.ai_service.AIService.generate_workout_plan")
    def test_generate_plan_success(self, mock_gen, client, db_session):
        """Generating a plan with a complete profile succeeds."""
        mock_gen.return_value = MOCK_WORKOUT_PLAN

        user = create_onboarded_user(db_session, email="workout@example.com")
        headers = get_auth_header(user)

        response = client.post("/api/v1/workout/generate", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "plan_id" in data
        assert "generated_at" in data
        assert len(data["plan"]["week"]) == 7


class TestGetWorkout:
    """Tests for GET /api/v1/workout/me"""

    @patch("app.services.ai_service.AIService.generate_workout_plan")
    def test_get_active_plan_success(self, mock_gen, client, db_session):
        """Getting the active plan returns it after generation."""
        mock_gen.return_value = MOCK_WORKOUT_PLAN

        user = create_onboarded_user(db_session, email="getplan@example.com")
        headers = get_auth_header(user)

        # Generate first
        client.post("/api/v1/workout/generate", headers=headers)

        # Then retrieve
        response = client.get("/api/v1/workout/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "plan_id" in data
        assert len(data["plan"]["week"]) == 7

    def test_get_active_plan_not_found(self, client, db_session):
        """Getting the active plan when none exists → 404."""
        user = create_onboarded_user(db_session, email="noplan@example.com")
        headers = get_auth_header(user)

        response = client.get("/api/v1/workout/me", headers=headers)
        assert response.status_code == 404
        assert "No workout plan found" in response.json()["detail"]


class TestDeleteWorkout:
    """Tests for DELETE /api/v1/workout/me"""

    @patch("app.services.ai_service.AIService.generate_workout_plan")
    def test_delete_plan_success(self, mock_gen, client, db_session):
        """Deleting the active plan sets is_active=False."""
        mock_gen.return_value = MOCK_WORKOUT_PLAN

        user = create_onboarded_user(db_session, email="delplan@example.com")
        headers = get_auth_header(user)

        # Generate first
        client.post("/api/v1/workout/generate", headers=headers)

        # Delete
        response = client.delete("/api/v1/workout/me", headers=headers)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

        # Verify it's gone
        get_response = client.get("/api/v1/workout/me", headers=headers)
        assert get_response.status_code == 404
