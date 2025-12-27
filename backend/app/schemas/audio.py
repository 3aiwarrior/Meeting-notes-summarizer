"""
Audio file schemas.

Pydantic models for audio upload and status endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AudioUploadResponse(BaseModel):
    """
    Response schema for audio upload.

    Attributes:
        id: Unique audio file identifier
        filename: Original filename
        file_size: File size in bytes
        status: Processing status
        created_at: Upload timestamp
    """

    id: UUID = Field(..., description="Unique audio file ID")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Processing status")
    created_at: datetime = Field(..., description="Upload timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "filename": "meeting_recording.webm",
                    "file_size": 1024000,
                    "status": "uploaded",
                    "created_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
        "from_attributes": True,
    }


class AudioStatusResponse(BaseModel):
    """
    Response schema for audio status check.

    Attributes:
        id: Unique audio file identifier
        filename: Original filename
        status: Current processing status
        duration_seconds: Audio duration if available
        error_message: Error details if failed
        transcription_id: ID of transcription if available
        summary_id: ID of summary if available
        created_at: Upload timestamp
        updated_at: Last update timestamp
    """

    id: UUID = Field(..., description="Unique audio file ID")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Processing status")
    duration_seconds: float | None = Field(None, description="Audio duration in seconds")
    error_message: str | None = Field(None, description="Error message if failed")
    transcription_id: UUID | None = Field(None, description="Transcription ID if available")
    summary_id: UUID | None = Field(None, description="Summary ID if available")
    created_at: datetime = Field(..., description="Upload timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "filename": "meeting_recording.webm",
                    "status": "completed",
                    "duration_seconds": 300.5,
                    "error_message": None,
                    "transcription_id": "660e8400-e29b-41d4-a716-446655440000",
                    "summary_id": "770e8400-e29b-41d4-a716-446655440000",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:35:00Z",
                }
            ]
        },
        "from_attributes": True,
    }
