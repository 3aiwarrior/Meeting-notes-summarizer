# Live Recording Feature - Technical Design

## Feature Overview

**User Story**: As a user, I want to click a "Listen" button to start recording audio from my microphone, and automatically get a transcription and summary when I stop recording.

## User Flow

1. User clicks **"Listen"** button
2. Browser requests microphone permission
3. Recording starts with visual indicator (animated icon, timer)
4. User speaks into microphone
5. User clicks **"Stop"** button
6. Audio is uploaded to backend
7. Backend transcribes via Whisper API
8. Backend summarizes via Claude API
9. Frontend displays results

## Architecture Decisions

### Option 1: REST-based (SELECTED)
- **Frontend**: Record audio → Create blob → Upload via multipart/form-data
- **Backend**: Receive file → Save → Background processing
- **Status Updates**: Frontend polls every 2 seconds
- **Pros**: Simple, stateless, works with existing infrastructure
- **Cons**: Slight delay in status updates

### Option 2: WebSocket-based
- **Frontend**: Stream audio chunks via WebSocket
- **Backend**: Real-time processing, push updates
- **Pros**: True real-time, better UX
- **Cons**: More complex, requires WebSocket infrastructure

**Decision**: Start with REST (Option 1) for MVP, add WebSocket later if needed.

## Backend API Design

### Endpoints

```
POST   /api/v1/audio/upload          # Upload audio file
GET    /api/v1/audio/{id}            # Get audio status
POST   /api/v1/transcription/start   # Start transcription job
GET    /api/v1/transcription/{id}    # Get transcription
POST   /api/v1/summary/generate      # Generate summary
GET    /api/v1/summary/{id}          # Get summary results
```

### Processing Pipeline

```
Audio Upload → Save File → Create DB Record
       ↓
Transcription Job → Call Whisper API → Save Text
       ↓
Summary Job → Call Claude API → Extract Data
       ↓
Return Results
```

## Frontend Design

### Components

**AudioRecorder.tsx**
- Manages MediaRecorder API
- Start/stop recording
- Audio blob creation
- Upload to backend

**ListenButton.tsx**
- Visual states: idle, recording, uploading, processing
- Timer display
- Permission handling

**ProcessingStatus.tsx**
- Polls backend for status
- Progress indicator
- Error handling

**SummaryDisplay.tsx**
- Shows transcription
- Displays key points, action items, decisions
- Copy/export functionality

### Recording Format

- **Format**: WebM with Opus codec (widely supported)
- **Fallback**: MP3 or WAV
- **Max Duration**: 2 hours (configurable)
- **Auto-stop**: Warn at 1:45, auto-stop at 2:00

## Data Flow

```
┌──────────────┐
│   Frontend   │
│  (Browser)   │
└──────┬───────┘
       │ 1. Click Listen
       │ 2. MediaRecorder captures audio
       │ 3. Stop → Create Blob
       │ 4. POST /api/v1/audio/upload
       ▼
┌──────────────┐
│   Backend    │
│   (FastAPI)  │
└──────┬───────┘
       │ 5. Save file, create AudioFile record
       │ 6. Call Whisper API
       ▼
┌──────────────┐
│ Whisper API  │
│  (OpenAI)    │
└──────┬───────┘
       │ 7. Return transcription
       ▼
┌──────────────┐
│   Backend    │
└──────┬───────┘
       │ 8. Save Transcription record
       │ 9. Call Claude API with prompt
       ▼
┌──────────────┐
│  Claude API  │
│ (Anthropic)  │
└──────┬───────┘
       │ 10. Return summary + structured data
       ▼
┌──────────────┐
│   Backend    │
└──────┬───────┘
       │ 11. Save Summary record
       │ 12. Update status = "completed"
       ▼
┌──────────────┐
│   Frontend   │
│  (Polling)   │
└──────────────┘
       │ 13. Fetch results
       │ 14. Display to user
```

## Implementation Plan

### Phase 1: Backend Audio Upload
- Audio upload endpoint
- File validation (format, size)
- Storage service
- Tests

### Phase 2: AI Integration
- Whisper transcription service
- Claude summarization service
- Background task processing
- Tests

### Phase 3: Frontend Recording
- React app setup (Vite + TypeScript)
- AudioRecorder component
- ListenButton component
- API integration

### Phase 4: Results Display
- SummaryDisplay component
- ProcessingStatus with polling
- Error handling
- UX polish

### Phase 5: Enhancements
- WebSocket support (optional)
- Audio visualization
- Download transcription/summary
- History of past recordings

## Technical Considerations

### Browser Compatibility
- **MediaRecorder API**: Chrome, Firefox, Edge, Safari 14.1+
- **Fallback**: Show error message for unsupported browsers

### Security
- Microphone permission handling
- CORS configuration for local dev
- File size limits (prevent abuse)
- Rate limiting on API endpoints

### Performance
- Chunked upload for large files
- Background processing (Celery + Redis)
- Database indexing on status fields
- Caching of results

### Error Handling
- Permission denied → Clear error message
- Upload failed → Retry logic
- API errors → User-friendly messages
- Timeout handling

## AI Prompt Design

### Whisper API Call
```python
response = openai.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="en",  # Auto-detect or specify
    response_format="json"
)
```

### Claude API Call
```python
response = anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    messages=[{
        "role": "user",
        "content": f"""Analyze this meeting transcription and provide:

1. A concise summary (2-3 paragraphs)
2. Key points discussed (bullet list)
3. Action items with owners if mentioned (structured list)
4. Decisions made (bullet list)
5. Participants mentioned (list of names)

Transcription:
{transcription_text}

Return response in JSON format:
{{
    "summary": "...",
    "key_points": ["...", "..."],
    "action_items": [{{"item": "...", "owner": "..."}}],
    "decisions": ["...", "..."],
    "participants": ["...", "..."]
}}
"""
    }]
)
```

## Success Metrics

- Recording works on all major browsers
- < 30 seconds total processing time for 5-minute audio
- 95%+ transcription accuracy (Whisper default)
- Clear, actionable summaries
- < 2% error rate
- Positive user feedback

## Future Enhancements

- Multi-language support
- Speaker diarization (who said what)
- Real-time transcription (streaming)
- Integration with calendar apps
- Export to PDF, Notion, Slack
- Search across past meetings
- Custom summary templates
