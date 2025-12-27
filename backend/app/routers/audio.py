"""
Audio router.

Endpoints for audio file upload and status retrieval.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.audio import AudioStatusResponse, AudioUploadResponse
from app.services.audio_service import AudioService

router = APIRouter()


@router.post("/upload", response_model=AudioUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(..., description="Audio file to upload"),
    db: Session = Depends(get_db),
) -> AudioUploadResponse:
    """
    Upload audio file for transcription and summarization.

    Accepts audio files in supported formats (webm, mp3, wav, m4a, mp4).
    Maximum file size configured in settings (default: 100MB).

    Args:
        file: Audio file upload
        db: Database session

    Returns:
        AudioUploadResponse: Created audio file information

    Raises:
        HTTPException 400: Invalid file format or missing file
        HTTPException 413: File too large
        HTTPException 500: Server error during upload
    """
    audio_service = AudioService(db)
    audio_file = await audio_service.upload_audio(file)

    return AudioUploadResponse(
        id=audio_file.id,
        filename=audio_file.filename,
        file_size=audio_file.file_size,
        status=audio_file.status,
        created_at=audio_file.created_at,
    )


@router.get("/{audio_id}", response_model=AudioStatusResponse, status_code=status.HTTP_200_OK)
async def get_audio_status(
    audio_id: UUID,
    db: Session = Depends(get_db),
) -> AudioStatusResponse:
    """
    Get audio file processing status.

    Returns current status and related transcription/summary IDs if available.

    Args:
        audio_id: UUID of audio file
        db: Database session

    Returns:
        AudioStatusResponse: Audio file status and metadata

    Raises:
        HTTPException 404: Audio file not found
    """
    audio_service = AudioService(db)
    audio_file = audio_service.get_audio_by_id(audio_id)

    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file {audio_id} not found",
        )

    # Get related transcription and summary IDs
    transcription_id = None
    summary_id = None

    if audio_file.transcription:
        transcription_id = audio_file.transcription.id
        if audio_file.transcription.summary:
            summary_id = audio_file.transcription.summary.id

    return AudioStatusResponse(
        id=audio_file.id,
        filename=audio_file.filename,
        status=audio_file.status,
        duration_seconds=audio_file.duration_seconds,
        error_message=audio_file.error_message,
        transcription_id=transcription_id,
        summary_id=summary_id,
        created_at=audio_file.created_at,
        updated_at=audio_file.updated_at,
    )
