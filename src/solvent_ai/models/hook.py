"""Result models for pre-commit hook."""

from dataclasses import dataclass


@dataclass
class HookResult:
    """Result of a pre-commit hook review.

    Attributes:
        passed: Whether the pre-commit check passed.
        feedback: AI-generated feedback about the staged files.
    """

    passed: bool
    feedback: str

    def __str__(self) -> str:
        """String representation of the hook result."""
        return self.feedback
