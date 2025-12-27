"""
Processing router.

Endpoints for triggering and managing audio processing pipeline.
"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.summary import SummaryResponse
from app.schemas.transcription import TranscriptionResponse
from app.services.audio_service import AudioService
from app.services.summary_service import SummaryService
from app.services.transcription_service import TranscriptionService

router = APIRouter()


async def process_audio_pipeline(audio_id: UUID, db: Session) -> None:
    """
    Background task to process audio file through transcription and summarization.

    Args:
        audio_id: UUID of audio file
        db: Database session
    """
    audio_service = AudioService(db)
    transcription_service = TranscriptionService(db)
    summary_service = SummaryService(db)

    # Get audio file
    audio_file = audio_service.get_audio_by_id(audio_id)
    if not audio_file:
        return

    try:
        # Step 1: Transcribe audio
        transcription = await transcription_service.transcribe_audio(audio_file)

        # Step 2: Generate summary
        await summary_service.generate_summary(transcription)

    except Exception as e:
        # Error handling is done in individual services
        print(f"Processing failed for audio {audio_id}: {str(e)}")


@router.post("/process/{audio_id}", status_code=status.HTTP_202_ACCEPTED)
async def start_processing(
    audio_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    """
    Start processing audio file (transcription + summarization).

    Triggers background processing pipeline. Use GET /audio/{audio_id}
    to check processing status.

    Args:
        audio_id: UUID of uploaded audio file
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        dict: Processing status message

    Raises:
        HTTPException 404: Audio file not found
        HTTPException 400: Audio already processed or processing
    """
    audio_service = AudioService(db)
    audio_file = audio_service.get_audio_by_id(audio_id)

    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file {audio_id} not found",
        )

    # Check if already processing or completed
    if audio_file.status in ["processing", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audio file is already {audio_file.status}",
        )

    # Add processing task to background
    background_tasks.add_task(process_audio_pipeline, audio_id, db)

    return {
        "message": "Processing started",
        "audio_id": str(audio_id),
        "status": "processing",
    }


@router.get(
    "/transcription/{transcription_id}",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_transcription(
    transcription_id: UUID,
    db: Session = Depends(get_db),
) -> TranscriptionResponse:
    """
    Get transcription by ID.

    Args:
        transcription_id: UUID of transcription
        db: Database session

    Returns:
        TranscriptionResponse: Transcription data

    Raises:
        HTTPException 404: Transcription not found
    """
    transcription_service = TranscriptionService(db)
    transcription = transcription_service.get_transcription_by_id(transcription_id)

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription {transcription_id} not found",
        )

    return TranscriptionResponse.model_validate(transcription)


@router.get(
    "/summary/{summary_id}",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_summary(
    summary_id: UUID,
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """
    Get summary by ID.

    Args:
        summary_id: UUID of summary
        db: Database session

    Returns:
        SummaryResponse: Summary data with structured information

    Raises:
        HTTPException 404: Summary not found
    """
    summary_service = SummaryService(db)
    summary = summary_service.get_summary_by_id(summary_id)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary {summary_id} not found",
        )

    return SummaryResponse.model_validate(summary)
