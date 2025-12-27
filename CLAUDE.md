# Claude Development Guidelines

## Project Awareness & Context

Before starting any work:
1. Review `PLANNING.md` for architecture and project goals
2. Check this file for coding conventions
3. Maintain consistency with established naming patterns

## Code Structure & Modularity

- **Max 500 lines per file** - Split into focused modules when approaching this limit
- **Feature-based organization** - Group related functionality together
- **Three-layer architecture** (Backend):
  - `routers/` - Thin HTTP layer (routing, status codes, metadata)
  - `services/` - Fat business logic layer
  - `schemas/` - Pydantic validation
- **Relative imports** within packages for clarity

## Testing & Reliability

- Write **pytest tests** for all new features
- Tests mirror main app structure in `/tests` directory
- Cover three scenarios: expected use, edge cases, failure modes
- Update tests when logic changes
- Run validation: `ruff` (linting), `pytest` (unit tests)

## Task Completion

- Mark completed work in task tracking immediately
- Document discovered sub-tasks or TODOs
- Never skip validation steps

## Style & Conventions

- **Language**: Python with PEP8 compliance
- **Formatting**: Black formatter
- **Type Hints**: Mandatory on all functions
- **Validation**: Pydantic models for all inputs/outputs
- **APIs**: FastAPI for REST endpoints
- **ORM**: SQLAlchemy/SQLModel for database
- **Environment**: python-dotenv for configuration
- **Documentation**: Google-style docstrings for all functions

## Documentation & Explainability

- Update `README.md` when features or dependencies change
- Add inline `# Reason:` comments for non-obvious logic
- Ensure mid-level developers can understand the codebase
- Document external API integrations

## AI Behavior Rules

- **Never assume missing context** - Ask clarifying questions
- **Don't hallucinate libraries** - Verify packages exist before using
- **Confirm file paths** exist before referencing them
- **Preserve existing code** unless explicitly changing it

## External API Integrations

### Anthropic Claude API
- Model: `claude-3-5-sonnet-20241022`
- Use for: Meeting summarization, key point extraction
- Rate limits: Monitor token usage

### OpenAI Whisper API
- Model: `whisper-1`
- Use for: Audio transcription
- Supported formats: mp3, wav, m4a, mp4
- Max file size: 25MB

## Validation Gates

**Level 1: Syntax & Style**
- ruff (linting)
- black (formatting)

**Level 2: Unit Tests**
- pytest with coverage

**Level 3: Integration**
- API endpoint testing
- End-to-end workflow validation
