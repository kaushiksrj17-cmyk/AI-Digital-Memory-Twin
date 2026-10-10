"""ECHO — AI Digital Memory Twin.

Research Title: Evidence-Grounded, Privacy-Preserving Multimodal AI for
                Interactive Digital Memory Preservation.

FastAPI Application Entrypoint.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.core.errors import register_error_handlers
from backend.app.api.v1.api import api_router
from backend.app.websockets.conversation_ws import ws_router
from database.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown event lifecycle."""
    setup_logging()
    logger.info("==================================================")
    logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.VERSION})")
    logger.info(f"Research Focus: {settings.RESEARCH_TITLE}")
    logger.info(f"Project Root Confined to: {settings.PROJECT_ROOT}")
    logger.info(f"Storage Root Confined to: {settings.STORAGE_ROOT}")
    logger.info("Ethical Safeguards: Active. Consciousness simulation prohibited.")
    logger.info("==================================================")

    # Ensure local storage directories exist within D:\ECHO
    Path(settings.STORAGE_ROOT).mkdir(parents=True, exist_ok=True)
    (Path(settings.STORAGE_ROOT) / "uploads").mkdir(parents=True, exist_ok=True)
    (Path(settings.STORAGE_ROOT) / "cache").mkdir(parents=True, exist_ok=True)
    (Path(settings.STORAGE_ROOT) / "encrypted").mkdir(parents=True, exist_ok=True)
    (Path(settings.PROJECT_ROOT) / "storage" / "voice" / "temp").mkdir(parents=True, exist_ok=True)
    (Path(settings.PROJECT_ROOT) / "storage" / "voice" / "profiles").mkdir(parents=True, exist_ok=True)
    (Path(settings.PROJECT_ROOT) / "storage" / "voice" / "recordings").mkdir(parents=True, exist_ok=True)

    yield

    logger.info("Shutting down ECHO application engine...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        f"**{settings.TAGLINE}**\n\n"
        f"**Research Title:** *{settings.RESEARCH_TITLE}*\n\n"
        "---\n\n"
        "### Ethical Notice\n"
        "ECHO is an AI-generated memorial representation created from authorized personal archives. "
        "It does not recreate consciousness, a soul, or the actual deceased person. "
        "All claims are strictly grounded in preserved evidence."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Error Handlers
register_error_handlers(app)

# Include API v1 and WebSocket Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
        "health_check": f"{settings.API_V1_STR}/health",
        "health_alias": "/health",
        "ethical_framework": settings.ETHICAL_DISCLAIMER_TEXT
    }


@app.get("/health", tags=["Root"], summary="Root Health Check Alias")
async def root_health_alias():
    """Root level health alias delegating to /api/v1/health check."""
    from backend.app.api.v1.endpoints.health import check_health
    return await check_health()

