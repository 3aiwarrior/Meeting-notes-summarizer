"""
Application settings and configuration.

Loads environment variables and provides typed configuration objects.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses pydantic-settings for validation and type conversion.
    """

    # Application
    app_name: str = "Meeting Notes Summarizer"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str

    # AI Services
    anthropic_api_key: str | None = None  # Optional: Only needed if using Claude
    openai_api_key: str
    claude_model: str = "claude-3-5-sonnet-20241022"
    gpt_model: str = "gpt-4o-mini"  # Reason: Cost-effective GPT model for summarization
    whisper_model: str = "whisper-1"

    # File Upload
    max_upload_size_mb: int = 100
    allowed_audio_formats: str = "mp3,wav,m4a,mp4,webm"
    upload_dir: str = "./uploads"

    # Processing
    max_audio_duration_minutes: int = 120
    processing_timeout_seconds: int = 600

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def allowed_audio_formats_list(self) -> list[str]:
        """Convert allowed audio formats string to list."""
        return [fmt.strip() for fmt in self.allowed_audio_formats.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert max upload size from MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024


# Singleton instance
settings = Settings()
