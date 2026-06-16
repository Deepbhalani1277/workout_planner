"""
Application configuration loaded from environment variables.

Uses Pydantic BaseSettings to automatically read from .env file and
validate types. Every config value is accessed via `get_settings()` — 
no secret is ever hardcoded in the codebase.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings object. Fields map 1:1 to the .env variables.
    Pydantic coerces values to the declared types automatically.
    """

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT Authentication ────────────────────────────────────
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Google OAuth 2.0 ──────────────────────────────────────
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # ── OpenAI API Keys ───────────────────────────────────────
    OPENAI_API_KEYS: str

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── SendGrid Email ────────────────────────────────────────
    SENDGRID_API_KEY: str

    # ── Frontend ──────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance so the .env file is only
    read once during the application lifetime.
    """
    return Settings()
