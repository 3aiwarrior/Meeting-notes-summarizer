"""
Audio file database model.

Stores metadata about uploaded audio files and their processing status.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AudioStatus(str, Enum):
    """Audio file processing status."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioFile(Base):
    """
    Audio file model for storing uploaded recordings.

    Tracks file metadata, processing status, and relationships to
    transcriptions and summaries.
    """

    __tablename__ = "audio_files"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # File metadata
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)  # Reason: Size in bytes
    mime_type = Column(String(100), nullable=False)
    duration_seconds = Column(Float, nullable=True)  # Reason: Extracted after upload

    # Processing status
    status = Column(
        String(20),
        nullable=False,
        default=AudioStatus.UPLOADED.value,
        index=True,
    )
    error_message = Column(String(1000), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    transcription = relationship(
        "Transcription",
        back_populates="audio_file",
        uselist=False,  # Reason: One-to-one relationship
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of audio file."""
        return f"<AudioFile {self.filename} ({self.status})>"
