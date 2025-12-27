"""
Summary schemas.

Pydantic models for summary endpoints.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """
    Response schema for summary.

    Attributes:
        id: Unique summary identifier
        transcription_id: ID of associated transcription
        summary_text: Main summary text
        key_points: List of key discussion points
        action_items: List of action items with owners
        decisions: List of decisions made
        participants: List of participant names
        tokens_used: AI tokens consumed
        model_used: AI model identifier
        status: Processing status
        created_at: Creation timestamp
    """

    id: UUID = Field(..., description="Unique summary ID")
    transcription_id: UUID = Field(..., description="Associated transcription ID")
    summary_text: str | None = Field(None, description="Summary text")
    key_points: list[str] | None = Field(None, description="Key discussion points")
    action_items: list[dict[str, Any]] | None = Field(None, description="Action items with owners")
    decisions: list[str] | None = Field(None, description="Decisions made")
    participants: list[str] | None = Field(None, description="Participant names")
    tokens_used: int | None = Field(None, description="AI tokens used")
    model_used: str | None = Field(None, description="AI model identifier")
    status: str = Field(..., description="Processing status")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "770e8400-e29b-41d4-a716-446655440000",
                    "transcription_id": "660e8400-e29b-41d4-a716-446655440000",
                    "summary_text": "The team discussed Q1 planning and resource allocation...",
                    "key_points": [
                        "Q1 budget approved",
                        "New hiring plan finalized",
                        "Project timeline adjusted",
                    ],
                    "action_items": [
                        {"item": "Prepare Q1 budget report", "owner": "John"},
                        {"item": "Schedule team onboarding", "owner": "Sarah"},
                    ],
                    "decisions": [
                        "Approved $50K additional budget",
                        "Delayed project launch by 2 weeks",
                    ],
                    "participants": ["John", "Sarah", "Mike", "Lisa"],
                    "tokens_used": 2500,
                    "model_used": "claude-3-5-sonnet-20241022",
                    "status": "completed",
                    "created_at": "2024-01-15T10:32:00Z",
                }
            ]
        },
        "from_attributes": True,
    }
