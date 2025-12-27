# Feature Documentation Template

## FEATURE

[Clear description of what's being implemented]

## EXAMPLES

[Code samples from `examples/` folder with explanations]

## DOCUMENTATION

[Links to external docs, API references, resources]

- Anthropic Claude API: https://docs.anthropic.com/
- OpenAI Whisper API: https://platform.openai.com/docs/guides/speech-to-text
- FastAPI: https://fastapi.tiangolo.com/
- React + Vite: https://vitejs.dev/guide/

## OTHER CONSIDERATIONS

[Gotchas, edge cases, common mistakes to avoid]

- Audio file size limits (25MB for Whisper API)
- Supported audio formats: mp3, wav, m4a, mp4
- Background task processing for long operations
- Polling vs WebSocket for status updates
- Token usage tracking for Claude API calls
- Error handling for external API failures
