"""
Transcription schemas.

Pydantic models for transcription endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    """
    Response schema for transcription.

    Attributes:
        id: Unique transcription identifier
        audio_file_id: ID of associated audio file
        full_text: Transcribed text
        language: Detected language
        status: Processing status
        processing_time_ms: Time taken to transcribe
        created_at: Creation timestamp
    """

    id: UUID = Field(..., description="Unique transcription ID")
    audio_file_id: UUID = Field(..., description="Associated audio file ID")
    full_text: str | None = Field(None, description="Transcribed text")
    language: str | None = Field(None, description="Detected language code")
    status: str = Field(..., description="Processing status")
    processing_time_ms: int | None = Field(None, description="Processing time in milliseconds")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "660e8400-e29b-41d4-a716-446655440000",
                    "audio_file_id": "550e8400-e29b-41d4-a716-446655440000",
                    "full_text": "Welcome everyone to today's meeting...",
                    "language": "en",
                    "status": "completed",
                    "processing_time_ms": 5420,
                    "created_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
        "from_attributes": True,
    }
