# Meeting Notes Summarizer

AI-powered microSaaS application for transcribing and summarizing meeting recordings using OpenAI Whisper and Anthropic Claude.

## Features

### Live Recording (NEW!)
- **One-Click Recording**: Click the "Listen" button to start recording from your microphone
- **Real-time Indicator**: Visual recording status with timer
- **Automatic Processing**: Stop recording to automatically transcribe and summarize
- **Instant Results**: Get structured meeting notes in under 2 minutes

### Core Features
- **Audio file upload** (MP3, WAV, M4A, MP4, WebM formats)
- **Automatic transcription** via OpenAI Whisper API
- **AI-powered summarization** with Anthropic Claude API
- **Structured data extraction**:
  - Meeting summary (2-3 paragraph overview)
  - Key points discussed
  - Action items with assignees
  - Decisions made
  - Participants mentioned
- **RESTful API** with FastAPI
- **React Frontend** with TypeScript
- **PostgreSQL database** for persistence
- **Docker-based deployment**

## Project Structure

```
meeting-notes-summarizer/
├── .claude/                    # Claude Code configuration
├── agents/                     # Custom agent implementations
├── skills/                     # Reusable skill modules
├── examples/                   # Example implementations and demos
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── core/              # Configuration and database
│   │   │   ├── settings.py    # Environment configuration
│   │   │   └── database.py    # SQLAlchemy setup
│   │   ├── models/            # Database models
│   │   │   ├── audio.py       # Audio file model
│   │   │   ├── transcription.py
│   │   │   └── summary.py
│   │   ├── routers/           # API endpoints
│   │   │   └── health.py      # Health check endpoint
│   │   ├── services/          # Business logic layer
│   │   ├── schemas/           # Pydantic validation models
│   │   │   └── health.py
│   │   └── main.py            # FastAPI application
│   ├── tests/                 # Pytest test suite
│   │   ├── conftest.py        # Test fixtures
│   │   └── routers/
│   │       └── test_health.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── ProcessingIndicator.tsx
│   │   │   └── SummaryDisplay.tsx
│   │   ├── services/          # API client
│   │   │   └── api.ts
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
├── .gitignore
├── CLAUDE.md                   # Development guidelines
├── PLANNING.md                 # Architecture documentation
└── README.md
```

## Technology Stack

**Backend:**
- Python 3.11
- FastAPI (API framework)
- SQLAlchemy (ORM)
- PostgreSQL 16 (Database)
- Pydantic (Validation)
- Pytest (Testing)

**AI Services:**
- OpenAI Whisper API (Transcription)
- Anthropic Claude API (Summarization)

**Infrastructure:**
- Docker & Docker Compose
- Redis (Background tasks)

**Frontend (Planned):**
- React 18
- TypeScript
- Vite
- React Query

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- OpenAI API Key
- Anthropic API Key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meeting-notes-summarizer
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-api-key-here
   OPENAI_API_KEY=sk-your-openai-api-key-here
   SECRET_KEY=your-secret-key-change-in-production
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL on port 5432
   - Redis on port 6379
   - FastAPI backend on port 8000

4. **Verify installation**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0",
     "database": "healthy"
   }
   ```

5. **Access API documentation**
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## Local Development

### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations** (after implementing Alembic)
   ```bash
   alembic upgrade head
   ```

4. **Start development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default: http://localhost:8000)
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   Frontend will be available at http://localhost:5173

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/routers/test_health.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Linting with ruff
ruff check .

# Formatting with black
black .

# Type checking (optional)
mypy app/
```

## Production Deployment

### Deploy to Hostinger VPS

For detailed production deployment instructions to Hostinger with domain configuration:

📘 **[Complete Deployment Guide](HOSTINGER_DEPLOYMENT.md)** - Step-by-step instructions for:
- VPS setup and Docker installation
- DNS configuration for your domain
- SSL/HTTPS certificate setup with Let's Encrypt
- Nginx reverse proxy configuration
- Environment variable setup
- Security hardening

✅ **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)** - Quick reference checklist

**Quick Overview:**
```bash
# 1. Configure DNS (in Hostinger panel)
# Add A records pointing to your VPS IP

# 2. On VPS: Install Docker & dependencies
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
apt install -y docker-compose nginx certbot python3-certbot-nginx

# 3. Deploy application
cd /var/www
git clone YOUR_REPO_URL meeting-notes-summarizer
cd meeting-notes-summarizer

# 4. Configure environment (update .env with production values)
nano .env  # Set DEBUG=False, update CORS_ORIGINS, generate SECRET_KEY

# 5. Build and start
docker-compose up -d --build

# 6. Configure Nginx + SSL
# See HOSTINGER_DEPLOYMENT.md for detailed Nginx configuration
certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

**Domain Structure:**
- `https://summarizer.sbs` → Frontend (React app)
- `https://api.summarizer.sbs` → Backend API
- `https://api.summarizer.sbs/api/docs` → API documentation

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/api/v1/health` | GET | Health check |
| `/api/docs` | GET | Swagger UI documentation |
| `/api/redoc` | GET | ReDoc documentation |

**Audio endpoints:**
- `POST /api/v1/audio/upload` - Upload audio file (multipart/form-data)
- `GET /api/v1/audio/{id}` - Get audio processing status

**Processing endpoints:**
- `POST /api/v1/process/{audio_id}` - Start transcription + summarization pipeline
- `GET /api/v1/transcription/{id}` - Get transcription by ID
- `GET /api/v1/summary/{id}` - Get summary with structured data

## Database Schema

### audio_files
- `id` (UUID, PK)
- `filename`, `file_path`, `file_size`, `mime_type`
- `duration_seconds`
- `status` (uploaded, processing, completed, failed)
- `created_at`, `updated_at`

### transcriptions
- `id` (UUID, PK)
- `audio_file_id` (FK)
- `full_text`, `language`, `confidence_score`
- `processing_time_ms`, `status`
- `created_at`, `updated_at`

### summaries
- `id` (UUID, PK)
- `transcription_id` (FK)
- `summary_text`
- `key_points` (JSONB)
- `action_items` (JSONB)
- `decisions` (JSONB)
- `participants` (JSONB)
- `meeting_date`, `tokens_used`, `model_used`
- `created_at`, `updated_at`

## Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude
- `OPENAI_API_KEY` - OpenAI API key for Whisper
- `SECRET_KEY` - Application secret key
- `DATABASE_URL` - PostgreSQL connection string

**Optional:**
- `MAX_UPLOAD_SIZE_MB` - Maximum file upload size (default: 100)
- `ALLOWED_AUDIO_FORMATS` - Supported formats (default: mp3,wav,m4a,mp4,webm)
- `CORS_ORIGINS` - Allowed CORS origins

## Development Guidelines

- **Code Style**: Follow PEP8, use Black formatter
- **Max File Length**: 500 lines per file
- **Type Hints**: Required on all functions
- **Documentation**: Google-style docstrings
- **Testing**: Pytest with >80% coverage
- **Architecture**: Three-layer pattern (routers → services → database)

See `CLAUDE.md` for detailed development guidelines.

## Roadmap

**Completed:**
- [x] Project structure and setup
- [x] Database models (Audio, Transcription, Summary)
- [x] FastAPI application skeleton
- [x] Health check endpoint
- [x] Docker configuration
- [x] Testing framework (pytest with 95% coverage)
- [x] Audio upload endpoint
- [x] Whisper API integration
- [x] Claude API integration
- [x] Background task processing
- [x] Frontend React application with TypeScript
- [x] Live recording feature with Listen button
- [x] Real-time status polling
- [x] Summary display with structured data

**In Progress:**
- [ ] Enhanced error handling and retries
- [ ] Audio file management (delete old files)
- [ ] User-friendly error messages

**Planned:**
- [ ] WebSocket support for real-time updates
- [ ] User authentication and accounts
- [ ] Meeting history and search
- [ ] Export to PDF, Notion, Slack
- [ ] Multi-language support
- [ ] Speaker diarization (who said what)
- [ ] API rate limiting
- [ ] Production deployment guide
- [ ] Cost estimation dashboard

## Contributing

1. Review `CLAUDE.md` for coding conventions
2. Check `PLANNING.md` for architecture details
3. Write tests for new features
4. Run validation before committing:
   ```bash
   ruff check . && black . && pytest
   ```

## License

MIT

## Support

For issues and feature requests, please create an issue in the repository.

---

**Generated with Claude Code** - AI-powered development assistant
