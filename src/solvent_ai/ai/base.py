"""Base class for AI client implementations."""

from abc import ABC, abstractmethod

from solvent_ai.models.file_info import FileInfo
from solvent_ai.rules.context import ContextRule


class AIClient(ABC):
    """Abstract base class for AI code review clients."""

    @abstractmethod
    def review_staged_files(
        self,
        file_info_dict: dict[str, FileInfo],
        context_rules: list[ContextRule] | None = None,
    ) -> str:
        """Review staged files using the AI provider.

        Args:
            file_info_dict: Dictionary mapping file paths to FileInfo objects
                containing diff, original content, and new content.
            context_rules: Optional list of ContextRule objects for file-specific
                context.

        Returns:
            AI-generated review feedback as a string.

        Raises:
            ValueError: If the API returns invalid feedback.
            Exception: For other API errors.
        """
        raise NotImplementedError
