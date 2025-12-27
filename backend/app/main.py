"""
Main FastAPI application entry point.

Configures routers, middleware, CORS, and lifecycle events.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.core.settings import settings
from app.routers import audio, health, processing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup: Initialize database tables
    init_db()
    yield
    # Shutdown: Clean up resources if needed


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=(
        ["*"] if settings.cors_allow_methods == "*" else settings.cors_allow_methods.split(",")
    ),
    allow_headers=(
        ["*"] if settings.cors_allow_headers == "*" else settings.cors_allow_headers.split(",")
    ),
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["audio"])
app.include_router(processing.router, prefix="/api/v1", tags=["processing"])


# Root endpoint
@app.get("/")
async def root() -> dict:
    """
    Root endpoint for API information.

    Returns:
        dict: API name and version
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
    }
