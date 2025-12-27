# Quick Start Guide

Get your Meeting Notes Summarizer running in 5 minutes!

## Prerequisites

- Docker and Docker Compose
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

## Step 1: Get API Keys

1. **OpenAI API Key**: Sign up at https://platform.openai.com/ and create an API key
2. **Anthropic API Key**: Sign up at https://console.anthropic.com/ and create an API key

## Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

Update these required fields in `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
OPENAI_API_KEY=sk-your-actual-openai-key-here
SECRET_KEY=your-random-secret-key-here  # Generate a random string
```

## Step 3: Start Services

```bash
# Start PostgreSQL, Redis, and Backend
docker-compose up -d

# Wait for services to be ready (~30 seconds)
docker-compose logs -f backend
```

You should see: `Application startup complete.`

## Step 4: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Step 5: Use the App!

1. Open http://localhost:5173 in your browser
2. Click the **"Listen"** button
3. Allow microphone access when prompted
4. Speak your meeting notes
5. Click **"Stop Recording"**
6. Wait ~1-2 minutes for processing
7. View your meeting summary!

## What You'll Get

Your meeting summary includes:

- **Overview**: 2-3 paragraph summary of the discussion
- **Key Points**: Main topics discussed (bullet list)
- **Action Items**: Tasks assigned with owners
- **Decisions**: Conclusions and agreements made
- **Participants**: Names mentioned in the meeting

## Troubleshooting

### Backend won't start
- Check API keys are valid in `.env`
- Ensure PostgreSQL is running: `docker-compose ps`
- View logs: `docker-compose logs backend`

### Frontend won't start
- Run `npm install` in frontend directory
- Check backend is running on port 8000

### Microphone access denied
- Allow microphone access in browser settings
- Try HTTPS (required by some browsers)

### Processing stuck
- Check backend logs: `docker-compose logs -f backend`
- Verify API keys have sufficient credits
- Check audio file was uploaded successfully

## Testing Without Recording

Upload a test audio file instead:

```bash
curl -X POST http://localhost:8000/api/v1/audio/upload \
  -F "file=@your-audio-file.mp3"

# Note the audio_id from response, then start processing:
curl -X POST http://localhost:8000/api/v1/process/{audio_id}

# Check status:
curl http://localhost:8000/api/v1/audio/{audio_id}
```

## API Documentation

Visit http://localhost:8000/api/docs for interactive API documentation.

## Cost Estimation

Approximate costs per meeting:

- **5-minute recording**: ~$0.03 (Whisper) + ~$0.05 (Claude) = **$0.08**
- **30-minute recording**: ~$0.18 (Whisper) + ~$0.10 (Claude) = **$0.28**
- **1-hour recording**: ~$0.36 (Whisper) + ~$0.15 (Claude) = **$0.51**

Based on OpenAI Whisper ($0.006/min) and Anthropic Claude pricing.

## Next Steps

- Read [PLANNING.md](PLANNING.md) for architecture details
- Check [CLAUDE.md](CLAUDE.md) for development guidelines
- See [LIVE_RECORDING_FEATURE.md](LIVE_RECORDING_FEATURE.md) for technical design

## Support

- Check existing issues: https://github.com/your-repo/issues
- API docs: http://localhost:8000/api/docs
- OpenAI docs: https://platform.openai.com/docs
- Anthropic docs: https://docs.anthropic.com/

---

Happy meeting summarizing! 🎤✨
