"""
FastAPI application entry point.

Sets up:
 • The FastAPI app instance with metadata for auto-docs
 • CORS middleware — locked to FRONTEND_URL (no wildcard)
 • Security-headers middleware (X-Content-Type-Options, X-Frame-Options,
   Strict-Transport-Security)
 • All v1 API routers under /api/v1
 • A simple /health endpoint for readiness probes
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

# ── Import routers ────────────────────────────────────────────
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.workout import router as workout_router
from app.api.v1.diet import router as diet_router

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


# ── Security-headers middleware ───────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """
    Adds hardened HTTP headers to every response:
     • X-Content-Type-Options: nosniff  — prevents MIME-sniffing
     • X-Frame-Options: DENY            — blocks click-jacking via iframes
     • Strict-Transport-Security        — forces HTTPS for 1 year
    """
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


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
