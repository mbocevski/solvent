"""Google Gemini API client for code review."""

import logging

from google.genai import Client

from solvent.ai.context import build_pre_commit_review_prompt
from solvent.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
    ) -> None:
        """Initialize Gemini client.

        Args:
            api_key: Gemini API key. If None, uses key from settings.
            model: Model name. If None, uses model from settings.
            temperature: Temperature for generation. If None, uses temperature from
                settings.
        """
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model or settings.gemini_model
        self.temperature = (
            temperature if temperature is not None else settings.gemini_temperature
        )

        self.client = Client(api_key=self.api_key)

        logger.debug(
            f"Initialized Gemini client with model: {self.model_name}, "
            f"temperature: {self.temperature}"
        )

    def review_staged_files(self, file_contents: dict[str, str]) -> str:
        """Review staged files using Gemini.

        Args:
            file_contents: Dictionary mapping file paths to their contents.

        Returns:
            AI-generated review feedback as a string.

        Raises:
            ValueError: If the API returns None feedback.
            Exception: For other API errors.
        """
        prompt = build_pre_commit_review_prompt(file_contents)

        def _validate_feedback(fb: str | None) -> str:
            """Validate that feedback is not None.

            Args:
                fb: Feedback string or None.

            Returns:
                Validated feedback string.

            Raises:
                ValueError: If feedback is None.
            """
            if fb is None:
                error_msg = "Gemini API returned None feedback"
                logger.error(error_msg)
                raise ValueError(error_msg)
            return fb

        try:
            logger.debug("Sending staged files review request to Gemini")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"temperature": self.temperature},
            )
            feedback = _validate_feedback(response.text)
            logger.debug("Received feedback from Gemini")
        except ValueError:
            raise
        except Exception:
            logger.exception("Error calling Gemini API")
            raise
        else:
            return feedback
