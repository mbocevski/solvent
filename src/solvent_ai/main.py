"""Main entry point for pre-commit hook."""

import argparse
import logging
import sys
from importlib.metadata import PackageNotFoundError, version

from solvent_ai.config import setup_logging
from solvent_ai.config.settings import get_settings
from solvent_ai.hook import run_pre_commit_review
from solvent_ai.hook.evaluator import strip_status_block


def get_version() -> str:
    """Get the package version.

    Returns:
        Package version string, or 'unknown' if not available.
    """
    try:
        return version("solvent")
    except PackageNotFoundError:
        # Fallback for development/not installed
        return "0.1.0"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="AI-powered pre-commit hook for code review using Google Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review staged files
  solvent

  # Verbose logging
  solvent --verbose

  # Show version
  solvent --version

  # Show help
  solvent --help

Environment Variables:
  SOLVENT_GEMINI_API_KEY    Required: Google Gemini API key
  SOLVENT_GEMINI_MODEL      Optional: Model name (default: gemini-2.5-flash)
  SOLVENT_GEMINI_TEMPERATURE Optional: Temperature 0.0-2.0 (default: 0.7)
  SOLVENT_LOG_LEVEL         Optional: DEBUG, INFO, WARNING, ERROR (default: INFO)

For more information, visit: https://github.com/mbocevski/solvent
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"solvent {get_version()}",
        help="Show version number and exit",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_const",
        const="DEBUG",
        dest="log_level",
        help="Enable verbose (DEBUG) logging output",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for pre-commit hook.

    Returns:
        Exit code: 0 if passed, 1 if failed.
    """
    # Parse command line arguments (--help and --version are handled by argparse)
    args = parse_args()

    # Set up logging
    settings = get_settings()
    # CLI flags override environment variable
    if args.log_level:
        log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    else:
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
