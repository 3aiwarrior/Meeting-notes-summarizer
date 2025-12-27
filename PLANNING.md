# Meeting Notes Summarizer - Architecture & Planning

## Project Overview

**MicroSaaS Application**: Audio meeting transcription and AI-powered summarization

**Value Proposition**: Upload meeting recordings, get automated transcription and intelligent summaries with key points, action items, and decisions extracted.

## Technology Stack

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + Vite + TypeScript
- **Database**: PostgreSQL 16
- **AI Services**:
  - OpenAI Whisper API (transcription)
  - Anthropic Claude API (summarization)
- **Deployment**: Docker containers + docker-compose
- **ORM**: SQLAlchemy
- **State Management**: React Context + React Query

## Architecture

### Backend (Three-Layer Pattern)

```
Request → Router → Service → Database
                ↓
            External APIs
        (Whisper, Claude)
```

**Routers** (`app/routers/`):
- `audio.py` - File upload, status retrieval
- `transcription.py` - Transcription endpoints
- `summary.py` - Summary generation
- `health.py` - Health checks

**Services** (`app/services/`):
- `audio_service.py` - File handling, validation
- `transcription_service.py` - Whisper API integration
- `summary_service.py` - Claude API integration
- `storage_service.py` - File system operations

**Models** (`app/models/`):
- `audio.py` - AudioFile SQLAlchemy model
- `transcription.py` - Transcription SQLAlchemy model
- `summary.py` - Summary SQLAlchemy model

**Schemas** (`app/schemas/`):
- Pydantic models for request/response validation

### Frontend (Feature-Based)

```
Pages → Components → Services → API
                  ↓
            Context (State)
```

**Pages**:
- `HomePage.tsx` - Landing page
- `UploadPage.tsx` - Audio upload + processing
- `ResultsPage.tsx` - Summary display

**Components**:
- `ui/` - Reusable UI elements
- `AudioUploader.tsx` - File upload interface
- `ProcessingStatus.tsx` - Progress indicator with polling
- `SummaryDisplay.tsx` - Results presentation
- `TranscriptionViewer.tsx` - Full transcript view

**Services**:
- `api.ts` - Axios/Fetch configuration
- `audioService.ts` - Audio upload API calls
- `summaryService.ts` - Summary retrieval

### Database Schema

**audio_files**:
- id (UUID, PK)
- filename, file_path, file_size, mime_type
- duration_seconds
- status (uploaded, processing, completed, failed)
- timestamps

**transcriptions**:
- id (UUID, PK)
- audio_file_id (FK → audio_files)
- full_text, language, confidence_score
- processing_time_ms
- status, error_message
- timestamps

**summaries**:
- id (UUID, PK)
- transcription_id (FK → transcriptions)
- summary_text
- key_points (JSONB array)
- action_items (JSONB array)
- decisions (JSONB array)
- participants (JSONB array)
- meeting_date
- tokens_used, model_used
- timestamps

## Processing Workflow

1. **Upload**: User uploads audio → Saved to `/uploads` → DB record created
2. **Transcription**: Background task calls Whisper API → Updates DB
3. **Summarization**: Background task calls Claude API → Extracts structured data → Updates DB
4. **Polling**: Frontend polls `/audio/{id}` every 3 seconds for status
5. **Display**: Results shown when status = "completed"

## API Contract

**Base URL**: `http://localhost:8000/api/v1`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/audio/upload` | POST | Upload audio file |
| `/audio/{id}` | GET | Get audio + processing status |
| `/transcription/start` | POST | Trigger transcription |
| `/transcription/{id}` | GET | Get transcription |
| `/summary/generate` | POST | Trigger summarization |
| `/summary/{id}` | GET | Get summary with structured data |

## External Dependencies

- **OpenAI Whisper API**: $0.006 per minute of audio
- **Anthropic Claude API**: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- **PostgreSQL**: Containerized database
- **Docker**: Container orchestration

## Development Workflow

1. Start Docker containers: `docker-compose up`
2. Backend runs on http://localhost:8000
3. Frontend runs on http://localhost:5173
4. PostgreSQL on port 5432

## Naming Conventions

- **Files**: lowercase_with_underscores.py (Python), PascalCase.tsx (React)
- **Classes**: PascalCase
- **Functions**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **React Components**: PascalCase
- **API Endpoints**: lowercase-hyphenated

## Success Criteria

- Audio upload working (< 100MB files)
- Transcription accurate (via Whisper)
- Summary quality high (Claude API)
- Structured data extraction (key points, action items, decisions)
- Clean UI with progress indication
- Docker deployment successful
- Tests passing (pytest)
- Code follows conventions (< 500 lines/file, type hints, docstrings)
