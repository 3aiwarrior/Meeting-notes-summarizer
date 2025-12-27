"""
Health check schemas.

Pydantic models for health check endpoints.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """
    Health check response schema.

    Attributes:
        status: Overall application status
        version: Application version
        database: Database connectivity status
    """

    status: str = Field(..., description="Overall application health status", examples=["healthy"])
    version: str = Field(..., description="Application version", examples=["0.1.0"])
    database: str = Field(
        ..., description="Database connectivity status", examples=["healthy", "unhealthy"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "0.1.0",
                    "database": "healthy",
                }
            ]
        }
    }
