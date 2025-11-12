"""Application settings and configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="SOLVENT_",
        case_sensitive=False,
        extra="ignore",
    )

    # AI Provider selection
    ai_provider: str = Field(
        default="gemini",
        description="AI provider to use (gemini, openai, anthropic)",
    )

    # Gemini API configuration (required if ai_provider=gemini)
    gemini_api_key: str | None = Field(
        default=None,
        description="Google Gemini API key (required if ai_provider=gemini)",
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model to use for reviews",
    )
    gemini_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for Gemini API calls",
    )

    # OpenAI API configuration (required if ai_provider=openai)
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key (required if ai_provider=openai)",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for reviews",
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for OpenAI API calls",
    )

    # Anthropic API configuration (required if ai_provider=anthropic)
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key (required if ai_provider=anthropic)",
    )
    anthropic_model: str = Field(
        default="claude-haiku-4-5",
        description="Anthropic model to use for reviews",
    )
    anthropic_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for Anthropic API calls (range: 0.0-1.0)",
    )

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # File size limits
    max_file_size: int = Field(
        default=1024 * 1024,  # 1MB in bytes
        description="Maximum file size in bytes to review (default: 1MB)",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern).

    Returns:
        Settings instance with configuration loaded from environment.
    """
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()  # pyright: ignore[reportCallIssue]
    return _settings
