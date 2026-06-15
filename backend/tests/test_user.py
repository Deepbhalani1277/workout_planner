"""
User endpoint tests.

Covers:
 • Get profile (authenticated, unauthenticated)
 • Save onboarding (success, invalid age)
 • Update onboarding (partial update)

All tests use a separate in-memory SQLite DB. No real
API calls or external services are involved.
"""

import pytest
from tests.conftest import create_test_user, get_auth_header


class TestGetProfile:
    """Tests for GET /api/v1/users/profile"""

    def test_get_profile_authenticated(self, client, db_session):
        """An authenticated user can retrieve their profile."""
        user = create_test_user(db_session, email="profile@example.com")
        headers = get_auth_header(user)

        response = client.get("/api/v1/users/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["is_complete"] is False  # Fresh profile, not onboarded yet

    def test_get_profile_unauthenticated(self, client):
        """Accessing profile without auth returns 401."""
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 401


class TestOnboarding:
    """Tests for POST /api/v1/users/onboarding"""

    def test_save_onboarding_success(self, client, db_session):
        """Submitting valid onboarding data sets is_complete=True."""
        user = create_test_user(db_session, email="onboard@example.com")
        headers = get_auth_header(user)

        response = client.post(
            "/api/v1/users/onboarding",
            headers=headers,
            json={
                "age": 25,
                "gender": "male",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "fitness_goal": "muscle_gain",
                "activity_level": "moderate",
                "equipment": ["dumbbells"],
                "diet_type": "non_vegetarian",
                "allergies": None,
                "budget_range": "3000_6000",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is True
        assert "Onboarding completed" in data["message"]

    def test_save_onboarding_invalid_age(self, client, db_session):
        """Onboarding rejects age outside valid range (13-80)."""
        user = create_test_user(db_session, email="age@example.com")
        headers = get_auth_header(user)

        response = client.post(
            "/api/v1/users/onboarding",
            headers=headers,
            json={
                "age": 5,  # Too young (min is 13)
                "gender": "male",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "fitness_goal": "muscle_gain",
                "activity_level": "moderate",
                "equipment": ["dumbbells"],
                "diet_type": "non_vegetarian",
                "allergies": None,
                "budget_range": "3000_6000",
            },
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_update_onboarding_partial(self, client, db_session):
        """Partial update only changes the provided fields."""
        user = create_test_user(db_session, email="partial@example.com")
        headers = get_auth_header(user)

        # First, complete onboarding
        client.post(
            "/api/v1/users/onboarding",
            headers=headers,
            json={
                "age": 25,
                "gender": "male",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "fitness_goal": "muscle_gain",
                "activity_level": "moderate",
                "equipment": ["dumbbells"],
                "diet_type": "non_vegetarian",
                "allergies": None,
                "budget_range": "3000_6000",
            },
        )

        # Now do a partial update — only weight_kg
        response = client.put(
            "/api/v1/users/onboarding",
            headers=headers,
            json={"weight_kg": 75.0},
        )
        assert response.status_code == 200
        assert "updated" in response.json()["message"]

        # Verify the update took effect and other fields are unchanged
        profile_resp = client.get("/api/v1/users/profile", headers=headers)
        profile_data = profile_resp.json()
        assert profile_data["weight_kg"] == 75.0
        assert profile_data["height_cm"] == 175.0  # Unchanged
        assert profile_data["age"] == 25  # Unchanged
