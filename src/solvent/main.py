"""Main entry point for pre-commit hook."""

import logging
import sys

from solvent.config import setup_logging
from solvent.config.settings import get_settings
from solvent.hook import run_pre_commit_review
from solvent.hook.evaluator import strip_status_block


def main() -> int:
    """Main entry point for pre-commit hook.

    Returns:
        Exit code: 0 if passed, 1 if failed.
    """
    # Set up logging
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    setup_logging(level=log_level)

    # Run pre-commit review
    result = run_pre_commit_review()

    # Print feedback (with status block removed for cleaner output)
    cleaned_feedback = strip_status_block(result.feedback)
    print(cleaned_feedback)

    # Return exit code based on result
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
