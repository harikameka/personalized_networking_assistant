# ============================================================================
# Personalized Networking Assistant — FastAPI Application Entry Point
# ============================================================================
# Creates the FastAPI application, registers middleware, mounts routers,
# and exposes a health-check endpoint.  Run via:
#
#     python -m app.main          (from the project root)
#     uvicorn app.main:app --reload
# ============================================================================

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import HealthResponse
from app.routers.conversation import router as conversation_router

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan (startup / shutdown hooks)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: ensure the data directory exists and log readiness.
    Shutdown: clean-up hook placeholder.
    """
    # ── Startup ─────────────────────────────────────────────────────────
    settings.get_data_dir()  # creates data/ if missing
    logger.info(
        "🚀 %s v%s is starting on %s:%d",
        settings.app_name,
        settings.app_version,
        settings.app_host,
        settings.app_port,
    )
    yield
    # ── Shutdown ────────────────────────────────────────────────────────
    logger.info("👋 %s is shutting down.", settings.app_name)


# ---------------------------------------------------------------------------
# FastAPI application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered networking assistant that generates smart conversation "
        "starters, verifies facts via Wikipedia, and tracks interaction history."
    ),
    lifespan=lifespan,
)

# ── CORS (allow the Streamlit frontend on any origin during development) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ──────────────────────────────────────────────────────────
app.include_router(conversation_router)


# ── Root health check ─────────────────────────────────────────────────────
@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root_health_check() -> HealthResponse:
    """Root endpoint — returns application health status."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc).astimezone().isoformat(),
    )


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def api_health_check() -> HealthResponse:
    """API health check at /api/health."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc).astimezone().isoformat(),
    )


# ---------------------------------------------------------------------------
# Direct execution: python -m app.main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level="info",
    )
