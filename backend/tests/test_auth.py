"""
Auth endpoint tests.

Covers:
 • Registration (success, duplicate email, weak password)
 • Login (success, wrong password, unverified email)
 • Token refresh (success, revoked token)

All tests use a separate in-memory SQLite DB and mock
Redis + email services. No real API calls are made.
"""

import pytest
from tests.conftest import (
    create_test_user,
    get_auth_header,
    get_refresh_token_for_user,
)


class TestRegister:
    """Tests for POST /api/v1/auth/register"""

    def test_register_success(self, client, db_session):
        """A new user can register with valid credentials."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Str0ng@Pass!",
                "full_name": "New User",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Registration successful" in data["message"]

    def test_register_duplicate_email(self, client, db_session):
        """Registration fails if the email is already taken."""
        create_test_user(db_session, email="dup@example.com")

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "password": "Str0ng@Pass!",
                "full_name": "Dup User",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_weak_password(self, client, db_session):
        """Registration fails if the password is too weak."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "short",
                "full_name": "Weak User",
            },
        )
        assert response.status_code == 400
        assert "Password" in response.json()["detail"]


class TestLogin:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success(self, client, db_session):
        """A verified user can log in with correct credentials."""
        create_test_user(
            db_session,
            email="login@example.com",
            password="Login@1234",
            is_verified=True,
        )

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "Login@1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client, db_session):
        """Login fails with incorrect password."""
        create_test_user(
            db_session,
            email="wrong@example.com",
            password="Correct@1234",
            is_verified=True,
        )

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "Wrong@5678"},
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_unverified_email(self, client, db_session):
        """Login fails if the user's email is not yet verified."""
        create_test_user(
            db_session,
            email="unverified@example.com",
            password="Valid@1234",
            is_verified=False,
        )

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "unverified@example.com", "password": "Valid@1234"},
        )
        assert response.status_code == 403
        assert "verify your email" in response.json()["detail"]


class TestRefreshToken:
    """Tests for POST /api/v1/auth/refresh"""

    def test_refresh_token_success(self, client, db_session):
        """A valid refresh token returns a new token pair."""
        user = create_test_user(
            db_session,
            email="refresh@example.com",
            password="Refresh@1234",
        )
        raw_refresh = get_refresh_token_for_user(db_session, user)

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": raw_refresh},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_revoked(self, client, db_session):
        """A revoked refresh token is rejected."""
        from app.models.refresh_token import RefreshToken
        from app.core.security import hash_token

        user = create_test_user(
            db_session,
            email="revoked@example.com",
            password="Revoked@1234",
        )
        raw_refresh = get_refresh_token_for_user(db_session, user)

        # Revoke the token
        token_h = hash_token(raw_refresh)
        db_token = (
            db_session.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_h)
            .first()
        )
        db_token.is_revoked = True
        db_session.commit()

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": raw_refresh},
        )
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"]
