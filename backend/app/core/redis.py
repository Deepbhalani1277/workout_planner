"""
Redis client and token-storage helpers.

Provides a shared Redis connection used for:
 • Email verification tokens (24hr TTL)
 • Password reset tokens (1hr TTL)
 • Rate limiting (future)
 • Caching AI responses (future)

The store_token / get_token / delete_token helpers abstract
away Redis commands so the rest of the codebase never imports
the redis library directly.
"""

import redis

from app.config import get_settings

settings = get_settings()

# ── Module-level connection ───────────────────────────────────
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def get_redis() -> redis.Redis:
    """Return the shared Redis client instance."""
    return redis_client


def store_token(key: str, value: str, ttl_seconds: int) -> None:
    """
    Store a key-value pair in Redis with a time-to-live.

    Used for verification and reset tokens — they auto-expire
    after the TTL so stale tokens cannot be replayed.
    """
    redis_client.setex(key, ttl_seconds, value)


def get_token(key: str) -> str | None:
    """
    Retrieve a value from Redis by key.

    Returns None if the key does not exist or has expired.
    """
    return redis_client.get(key)


def delete_token(key: str) -> None:
    """
    Delete a key from Redis.

    Called after a token has been successfully consumed
    (e.g. email verified, password reset) to prevent reuse.
    """
    redis_client.delete(key)
