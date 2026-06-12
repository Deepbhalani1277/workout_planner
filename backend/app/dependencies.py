"""
Shared FastAPI dependencies.

Centralises reusable dependencies (auth, database, config) so that
routers and services can import them from one place.
"""

from app.config import Settings, get_settings
from app.db.session import get_db

__all__ = ["get_db", "get_settings", "Settings"]
