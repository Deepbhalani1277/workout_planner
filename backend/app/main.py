"""
FastAPI application entry point.

Sets up:
 • The FastAPI app instance with metadata for auto-docs
 • CORS middleware — locked to FRONTEND_URL (no wildcard)
 • Security-headers middleware (X-Content-Type-Options, X-Frame-Options,
   Strict-Transport-Security, X-XSS-Protection, Referrer-Policy)
 • Rate-limiting middleware (Redis-backed, per-IP and per-user)
 • Request-size middleware (rejects bodies > 1 MB)
 • All v1 API routers under /api/v1
 • A simple /health endpoint for readiness probes
"""

import time

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings

# ── Import routers ────────────────────────────────────────────
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.workout import router as workout_router
from app.api.v1.diet import router as diet_router

# ── Import DB Base (registers all models for SQLAlchemy) ──────
import app.db.base  # noqa: F401

settings = get_settings()

# ── App instance ──────────────────────────────────────────────
app = FastAPI(
    title="Personalized Workout Planner",
    description="AI-powered workout and diet planning API",
    version="1.0.0",
)

# ── CORS middleware ───────────────────────────────────────────
# Only the configured frontend origin is allowed — never "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════
#  MIDDLEWARE 1: Security Headers
# ═══════════════════════════════════════════════════════════════

@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """
    Adds hardened HTTP headers to every response:
     • X-Content-Type-Options: nosniff  — prevents MIME-sniffing
     • X-Frame-Options: DENY            — blocks click-jacking via iframes
     • Strict-Transport-Security        — forces HTTPS for 1 year
     • X-XSS-Protection                 — enables browser XSS filter
     • Referrer-Policy                  — limits referrer information leakage
    """
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ═══════════════════════════════════════════════════════════════
#  MIDDLEWARE 2: Request Size Limiter
# ═══════════════════════════════════════════════════════════════

MAX_REQUEST_BODY_SIZE = 1 * 1024 * 1024  # 1 MB


@app.middleware("http")
async def request_size_limiter(request: Request, call_next) -> Response:
    """
    Reject requests with a body larger than 1 MB.

    Reads the Content-Length header first (fast path). If not
    present, lets the request through — downstream body parsing
    will enforce limits.

    Returns 413 Request Entity Too Large when exceeded.
    """
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_SIZE:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Request body too large. Maximum size is 1 MB."},
        )
    return await call_next(request)


# ═══════════════════════════════════════════════════════════════
#  MIDDLEWARE 3: Rate Limiting (Redis-backed)
# ═══════════════════════════════════════════════════════════════

# Rate limit rules:
#   key_prefix           limit   window_seconds
RATE_LIMIT_RULES = {
    "/api/v1/auth/login":        (20, 15 * 60),     # 20 per IP per 15 min
    "/api/v1/auth/register":     (20, 60 * 60),     # 20 per IP per hour
    "/api/v1/workout/generate":  (100, 24 * 60 * 60), # 100 per user per day (increased for dev testing)
    "/api/v1/diet/generate":     (100, 24 * 60 * 60), # 100 per user per day (increased for dev testing)
}

# Global rate limit: 100 requests per IP per minute
GLOBAL_RATE_LIMIT = 100
GLOBAL_RATE_WINDOW = 60  # seconds


def _get_redis_for_rate_limit():
    """
    Lazily import and return the Redis client.

    Importing at module level would fail during testing when
    Redis is not available. Lazy import + try/except lets the
    app start even if Redis is temporarily down.
    """
    try:
        from app.core.redis import get_redis
        return get_redis()
    except Exception:
        return None


def _get_client_ip(request: Request) -> str:
    """
    Extract the real client IP from the request.

    Checks X-Forwarded-For first (for proxied setups),
    falls back to the direct client address.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(redis_client, key: str, limit: int, window: int) -> bool:
    """
    Check whether a rate limit key has exceeded its limit.

    Uses Redis INCR + EXPIRE for atomic counter management:
     1. Increment the counter for the key
     2. If it's the first request in this window, set the TTL
     3. Return True if the limit is exceeded

    Returns False (allow) if Redis is unavailable — we degrade
    gracefully rather than blocking all requests.
    """
    if not redis_client:
        return False  # Degrade gracefully

    try:
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, window)
        return current > limit
    except Exception:
        return False  # Degrade gracefully on Redis errors


@app.middleware("http")
async def rate_limiter(request: Request, call_next) -> Response:
    """
    Redis-backed rate limiting middleware.

    Applies:
     • Endpoint-specific limits (login, register, generate)
     • Global per-IP limit (100 req/min)

    Returns 429 Too Many Requests when any limit is exceeded.
    Degrades gracefully if Redis is unavailable (allows all requests).
    """
    redis_client = _get_redis_for_rate_limit()
    path = request.url.path
    client_ip = _get_client_ip(request)

    # ── Endpoint-specific rate limits ────────────────────────
    for rule_path, (limit, window) in RATE_LIMIT_RULES.items():
        if path == rule_path:
            # For /workout/generate and /diet/generate, rate limit per user
            # For auth endpoints, rate limit per IP
            if "generate" in rule_path:
                # Per-user rate limiting requires auth — extract user_id
                # from the Authorization header if present
                auth_header = request.headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ", 1)[1]
                    try:
                        from app.core.security import decode_token
                        payload = decode_token(token, settings.SECRET_KEY)
                        user_id = payload.get("sub", client_ip)
                        key = f"rl:{rule_path}:user:{user_id}"
                    except Exception:
                        key = f"rl:{rule_path}:ip:{client_ip}"
                else:
                    key = f"rl:{rule_path}:ip:{client_ip}"
            else:
                key = f"rl:{rule_path}:ip:{client_ip}"

            if _check_rate_limit(redis_client, key, limit, window):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too many requests. Please try again later."},
                )
            break

    # ── Global rate limit (100 req/IP/min) ───────────────────
    global_key = f"rl:global:ip:{client_ip}"
    if _check_rate_limit(redis_client, global_key, GLOBAL_RATE_LIMIT, GLOBAL_RATE_WINDOW):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later."},
        )

    return await call_next(request)


# ── Register routers ─────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(workout_router, prefix="/api/v1")
app.include_router(diet_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Lightweight readiness probe.
    Returns 200 with status 'healthy' when the service is up.
    """
    return {"status": "healthy"}
