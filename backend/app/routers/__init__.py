"""
Routers package.

Exports all API routers for the application.
"""

from app.routers import audio, health, processing

__all__ = ["audio", "health", "processing"]
