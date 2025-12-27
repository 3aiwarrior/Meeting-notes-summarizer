"""
Summary database model.

Stores AI-generated summaries with structured data extraction.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SummaryStatus(str, Enum):
    """Summary generation status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Summary(Base):
    """
    Summary model for storing Claude API results.

    Contains AI-generated summaries plus structured data like
    key points, action items, decisions, and participants.
    """

    __tablename__ = "summaries"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key to transcription
    transcription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transcriptions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Reason: One summary per transcription
        index=True,
    )

    # Summary content
    summary_text = Column(Text, nullable=True)

    # Structured data (JSON for cross-database compatibility)
    # Reason: Uses JSONB on PostgreSQL, JSON on SQLite for testing
    key_points = Column(JSON, nullable=True)  # Reason: Array of strings
    action_items = Column(JSON, nullable=True)  # Reason: Array of objects
    decisions = Column(JSON, nullable=True)  # Reason: Array of strings
    participants = Column(JSON, nullable=True)  # Reason: Array of strings

    # Meeting metadata
    meeting_date = Column(Date, nullable=True)

    # AI usage tracking
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)

    # Processing metadata
    status = Column(
        String(20),
        nullable=False,
        default=SummaryStatus.PENDING.value,
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
    transcription = relationship("Transcription", back_populates="summary")

    def __repr__(self) -> str:
        """String representation of summary."""
        preview = self.summary_text[:50] if self.summary_text else "No summary"
        return f"<Summary {self.id} ({self.status}): {preview}...>"
