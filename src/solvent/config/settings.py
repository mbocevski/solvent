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

    # Gemini API configuration
    gemini_api_key: str = Field(
        ...,
        description="Google Gemini API key",
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

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
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
