"""
Summary service using OpenAI GPT API.

Handles meeting summary generation and structured data extraction.
"""

import json
from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.audio import AudioStatus
from app.models.summary import Summary, SummaryStatus
from app.models.transcription import Transcription


class SummaryService:
    """
    Service for generating meeting summaries using OpenAI GPT API.

    Manages summary generation and structured data extraction.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize summary service.

        Args:
            db: Database session
        """
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def generate_summary(self, transcription: Transcription) -> Summary:
        """
        Generate summary from transcription using OpenAI GPT API.

        Args:
            transcription: Transcription database record

        Returns:
            Summary: Created summary record

        Raises:
            Exception: If summary generation fails
        """
        # Create summary record
        summary = Summary(
            transcription_id=transcription.id,
            status=SummaryStatus.IN_PROGRESS.value,
            model_used=settings.gpt_model,
        )
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)

        try:
            # Create prompt for GPT
            prompt = self._create_summary_prompt(transcription.full_text)

            # Call OpenAI GPT API
            response = self.client.chat.completions.create(
                model=settings.gpt_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise meeting notes assistant. Extract ONLY essential information. Be extremely concise. Return valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1200,  # Reason: Reduced for more concise output
                temperature=0.5,  # Reason: Lower temperature for more focused responses
            )

            # Extract response text
            response_text = response.choices[0].message.content

            # Parse JSON response
            try:
                summary_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: Use raw text if JSON parsing fails
                summary_data = {
                    "summary": response_text,
                    "key_points": [],
                    "action_items": [],
                    "decisions": [],
                    "participants": [],
                }

            # Update summary record
            summary.summary_text = summary_data.get("summary", "")
            summary.key_points = summary_data.get("key_points", [])
            summary.action_items = summary_data.get("action_items", [])
            summary.decisions = summary_data.get("decisions", [])
            summary.participants = summary_data.get("participants", [])
            summary.tokens_used = response.usage.total_tokens
            summary.status = SummaryStatus.COMPLETED.value

            # Update audio file status to completed
            if transcription.audio_file:
                transcription.audio_file.status = AudioStatus.COMPLETED.value

            self.db.commit()
            self.db.refresh(summary)

            return summary

        except Exception as e:
            # Update summary with error
            summary.status = SummaryStatus.FAILED.value
            summary.error_message = str(e)

            # Update audio file status
            if transcription.audio_file:
                transcription.audio_file.status = AudioStatus.FAILED.value
                transcription.audio_file.error_message = f"Summary generation failed: {str(e)}"

            self.db.commit()
            raise

    def get_summary_by_id(self, summary_id: UUID) -> Summary | None:
        """
        Get summary by ID.

        Args:
            summary_id: UUID of summary

        Returns:
            Optional[Summary]: Summary or None if not found
        """
        return self.db.query(Summary).filter(Summary.id == summary_id).first()

    def get_summary_by_transcription_id(self, transcription_id: UUID) -> Summary | None:
        """
        Get summary by transcription ID.

        Args:
            transcription_id: UUID of transcription

        Returns:
            Optional[Summary]: Summary or None if not found
        """
        return self.db.query(Summary).filter(Summary.transcription_id == transcription_id).first()

    def _create_summary_prompt(self, transcription_text: str) -> str:
        """
        Create prompt for GPT API - optimized for concise output.

        Args:
            transcription_text: Full transcription text

        Returns:
            str: Formatted prompt
        """
        return f"""Analyze this meeting transcription and provide a BRIEF, PRECISE summary.

BE CONCISE - Keep everything short and essential:

1. **Summary**: 2-3 sentences maximum capturing the core purpose and outcome
2. **Key Points**: Top 3-5 points only, each one sentence
3. **Action Items**: List only clear tasks with owners
4. **Decisions**: Top 3 critical decisions only
5. **Participants**: Names mentioned in the meeting

Transcription:
{transcription_text}

IMPORTANT: Return valid JSON. Be extremely concise - NO fluff, NO repetition:
{{
    "summary": "Brief 2-3 sentence overview",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "action_items": [{{"item": "Brief task", "owner": "Name"}}],
    "decisions": ["Decision 1", "Decision 2"],
    "participants": ["Name 1", "Name 2"]
}}

If any section has no data, use an empty array []. Focus on brevity and precision."""
