"""
Google OAuth helper.

Verifies the Google ID token received from the frontend's
Google Sign-In button against Google's public keys, and
extracts the user's email and name.
"""

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.config import get_settings

settings = get_settings()


def verify_google_token(credential: str) -> dict | None:
    """
    Verify a Google ID token and return the payload.

    Returns a dict with keys like 'email', 'name', 'sub' (Google user id)
    on success, or None if verification fails.
    """
    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        return id_info
    except ValueError:
        return None
