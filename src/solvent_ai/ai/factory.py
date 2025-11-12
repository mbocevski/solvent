"""Factory for creating AI client instances."""

import logging

from solvent_ai.ai.base import AIClient
from solvent_ai.config import get_settings

logger = logging.getLogger(__name__)


def create_ai_client() -> AIClient:
    """Create an AI client based on configured provider.

    Returns:
        An instance of the configured AI client.

    Raises:
        ValueError: If the configured provider is not supported or required
            API key is missing.
    """
    settings = get_settings()
    provider = settings.ai_provider.lower()

    if provider == "gemini":
        from solvent_ai.ai.gemini import GeminiClient  # noqa: PLC0415

        if not settings.gemini_api_key:
            raise ValueError(
                "Gemini API key is required when ai_provider=gemini. "
                "Set SOLVENT_GEMINI_API_KEY environment variable."
            )
        return GeminiClient()
    if provider == "openai":
        from solvent_ai.ai.openai import OpenAIClient  # noqa: PLC0415

        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key is required when ai_provider=openai. "
                "Set SOLVENT_OPENAI_API_KEY environment variable."
            )
        return OpenAIClient()
    raise ValueError(
        f"Unsupported AI provider: {provider}. Supported providers: gemini, openai"
    )
