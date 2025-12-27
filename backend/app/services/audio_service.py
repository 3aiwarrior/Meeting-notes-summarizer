"""
Audio service for handling audio file operations.

Manages audio file uploads, validation, and processing coordination.
"""

from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.audio import AudioFile, AudioStatus
from app.services.storage_service import StorageService


class AudioService:
    """
    Service for audio file operations.

    Handles upload, validation, storage, and database operations.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize audio service.

        Args:
            db: Database session
        """
        self.db = db
        self.storage = StorageService()

    async def upload_audio(self, file: UploadFile) -> AudioFile:
        """
        Upload and save audio file.

        Args:
            file: Uploaded audio file

        Returns:
            AudioFile: Created database record

        Raises:
            HTTPException: If validation fails or upload errors
        """
        # Validate file
        self._validate_audio_file(file)

        # Read file content
        file_content = await file.read()

        # Check file size
        if len(file_content) > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.max_upload_size_mb}MB",
            )

        # Save file to disk
        try:
            file_path, unique_filename = self.storage.save_audio_file(
                file_content, file.filename or "recording.webm"
            )
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}",
            )

        # Create database record
        audio_file = AudioFile(
            filename=file.filename or "recording.webm",
            file_path=file_path,
            file_size=len(file_content),
            mime_type=file.content_type or "audio/webm",
            status=AudioStatus.UPLOADED.value,
        )

        self.db.add(audio_file)
        self.db.commit()
        self.db.refresh(audio_file)

        return audio_file

    def get_audio_by_id(self, audio_id: UUID) -> AudioFile | None:
        """
        Get audio file by ID.

        Args:
            audio_id: UUID of audio file

        Returns:
            Optional[AudioFile]: Audio file or None if not found
        """
        return self.db.query(AudioFile).filter(AudioFile.id == audio_id).first()

    def update_audio_status(
        self, audio_id: UUID, status: AudioStatus, error_message: str | None = None
    ) -> AudioFile | None:
        """
        Update audio file processing status.

        Args:
            audio_id: UUID of audio file
            status: New status
            error_message: Error message if status is FAILED

        Returns:
            Optional[AudioFile]: Updated audio file or None if not found
        """
        audio_file = self.get_audio_by_id(audio_id)
        if not audio_file:
            return None

        audio_file.status = status.value
        if error_message:
            audio_file.error_message = error_message

        self.db.commit()
        self.db.refresh(audio_file)

        return audio_file

    def _validate_audio_file(self, file: UploadFile) -> None:
        """
        Validate uploaded audio file.

        Args:
            file: Uploaded file

        Raises:
            HTTPException: If validation fails
        """
        # Check if file exists
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided",
            )

        # Check filename
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # Check file extension
        file_extension = file.filename.split(".")[-1].lower()
        allowed_formats = settings.allowed_audio_formats_list

        if file_extension not in allowed_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed: {', '.join(allowed_formats)}",
            )

        # Validate content type
        if file.content_type and not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file",
            )
