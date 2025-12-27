"""
Transcription database model.

Stores transcribed text from audio files via Whisper API.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TranscriptionStatus(str, Enum):
    """Transcription processing status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Transcription(Base):
    """
    Transcription model for storing Whisper API results.

    Links to audio files and contains full transcribed text plus metadata.
    """

    __tablename__ = "transcriptions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key to audio file
    audio_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("audio_files.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Reason: One transcription per audio file
        index=True,
    )

    # Transcription data
    full_text = Column(Text, nullable=True)  # Reason: Can be large text
    language = Column(String(10), nullable=True)  # Reason: ISO language code
    confidence_score = Column(Float, nullable=True)  # Reason: 0.0 to 1.0

    # Processing metadata
    processing_time_ms = Column(Integer, nullable=True)
    status = Column(
        String(20),
        nullable=False,
        default=TranscriptionStatus.PENDING.value,
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
    audio_file = relationship("AudioFile", back_populates="transcription")
    summary = relationship(
        "Summary",
        back_populates="transcription",
        uselist=False,  # Reason: One-to-one relationship
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of transcription."""
        preview = self.full_text[:50] if self.full_text else "No text"
        return f"<Transcription {self.id} ({self.status}): {preview}...>"
