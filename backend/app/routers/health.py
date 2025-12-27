"""
Health check router.

Provides endpoints for monitoring application health and database connectivity.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.settings import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint.

    Verifies application is running and database is accessible.

    Args:
        db: Database session dependency

    Returns:
        HealthResponse: Health status with database connectivity

    Raises:
        HTTPException: If database is unreachable
    """
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        database_status = "healthy"
    except Exception as e:
        database_status = "unhealthy"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database=database_status,
    )
