"""OpenAI API client for code review."""

import logging

from openai import OpenAI

from solvent_ai.ai.base import AIClient
from solvent_ai.ai.context import build_pre_commit_review_prompt
from solvent_ai.ai.retry import retry_with_backoff
from solvent_ai.config import get_settings
from solvent_ai.models.file_info import FileInfo
from solvent_ai.rules.context import ContextRule

logger = logging.getLogger(__name__)


class OpenAIClient(AIClient):
    """Client for interacting with OpenAI API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key. If None, uses key from settings.
            model: Model name. If None, uses model from settings.
            temperature: Temperature for generation. If None, uses temperature from
                settings.
            max_tokens: Maximum tokens. If None, uses value from general max_tokens
                setting, or model default if not set.

        Raises:
            ValueError: If API key is not provided.
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model_name = model or settings.openai_model
        self.temperature = (
            temperature if temperature is not None else settings.openai_temperature
        )
        self.max_tokens = max_tokens if max_tokens is not None else settings.max_tokens

        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set SOLVENT_OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key)

        logger.debug(
            f"Initialized OpenAI client with model: {self.model_name}, "
            f"temperature: {self.temperature}, max_tokens: {self.max_tokens}"
        )

    def review_staged_files(
        self,
        file_info_dict: dict[str, FileInfo],
        context_rules: list[ContextRule] | None = None,
    ) -> str:
        """Review staged files using OpenAI.

        Args:
            file_info_dict: Dictionary mapping file paths to FileInfo objects
                containing diff, original content, and new content.
            context_rules: Optional list of ContextRule objects for file-specific
                context.

        Returns:
            AI-generated review feedback as a string.

        Raises:
            ValueError: If the API returns None feedback.
            Exception: For other API errors.
        """
        prompt = build_pre_commit_review_prompt(file_info_dict, context_rules)

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
                error_msg = "OpenAI API returned None feedback"
                logger.error(error_msg)
                raise ValueError(error_msg)
            return fb

        def _call_api() -> str:
            """Make the API call (used for retry logic).

            Returns:
                AI-generated feedback string.

            Raises:
                ValueError: If the API returns None feedback.
                Exception: For other API errors.
            """
            logger.debug("Sending staged files review request to OpenAI")
            request_params = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
            }
            if self.max_tokens is not None:
                request_params["max_tokens"] = self.max_tokens
            response = self.client.chat.completions.create(**request_params)
            feedback = _validate_feedback(
                response.choices[0].message.content if response.choices else None
            )
            logger.debug("Received feedback from OpenAI")
            return feedback

        try:
            # Retry with exponential backoff for transient errors
            return retry_with_backoff(
                _call_api, operation_name="OpenAI API review request"
            )
        except ValueError:
            # Don't retry validation errors
            raise
        except Exception:
            logger.exception("Error calling OpenAI API after retries")
            raise
