"""
Transcription service using OpenAI Whisper API.

Handles audio transcription through the Whisper API.
"""

import time
from uuid import UUID

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.audio import AudioFile, AudioStatus
from app.models.transcription import Transcription, TranscriptionStatus


class TranscriptionService:
    """
    Service for audio transcription using Whisper API.

    Manages transcription jobs and Whisper API integration.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize transcription service.

        Args:
            db: Database session
        """
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def transcribe_audio(self, audio_file: AudioFile) -> Transcription:
        """
        Transcribe audio file using Whisper API.

        Args:
            audio_file: Audio file database record

        Returns:
            Transcription: Created transcription record

        Raises:
            Exception: If transcription fails
        """
        # Create transcription record
        transcription = Transcription(
            audio_file_id=audio_file.id,
            status=TranscriptionStatus.IN_PROGRESS.value,
        )
        self.db.add(transcription)
        self.db.commit()
        self.db.refresh(transcription)

        # Update audio status
        audio_file.status = AudioStatus.PROCESSING.value
        self.db.commit()

        start_time = time.time()

        try:
            # Call Whisper API
            with open(audio_file.file_path, "rb") as audio:
                response = self.client.audio.transcriptions.create(
                    model=settings.whisper_model,
                    file=audio,
                    response_format="verbose_json",  # Reason: Get additional metadata
                )

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Update transcription record
            transcription.full_text = response.text
            transcription.language = getattr(response, "language", None)
            transcription.processing_time_ms = processing_time_ms
            transcription.status = TranscriptionStatus.COMPLETED.value

            # Update audio file duration if available
            if hasattr(response, "duration"):
                audio_file.duration_seconds = response.duration

            self.db.commit()
            self.db.refresh(transcription)

            return transcription

        except Exception as e:
            # Update transcription with error
            transcription.status = TranscriptionStatus.FAILED.value
            transcription.error_message = str(e)

            # Update audio file status
            audio_file.status = AudioStatus.FAILED.value
            audio_file.error_message = f"Transcription failed: {str(e)}"

            self.db.commit()
            raise

    def get_transcription_by_id(self, transcription_id: UUID) -> Transcription | None:
        """
        Get transcription by ID.

        Args:
            transcription_id: UUID of transcription

        Returns:
            Optional[Transcription]: Transcription or None if not found
        """
        return self.db.query(Transcription).filter(Transcription.id == transcription_id).first()

    def get_transcription_by_audio_id(self, audio_id: UUID) -> Transcription | None:
        """
        Get transcription by audio file ID.

        Args:
            audio_id: UUID of audio file

        Returns:
            Optional[Transcription]: Transcription or None if not found
        """
        return self.db.query(Transcription).filter(Transcription.audio_file_id == audio_id).first()
