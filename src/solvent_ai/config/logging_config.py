"""Logging configuration for solvent."""

import logging
import sys


def setup_logging(level: int | None = None) -> None:
    """Set up logging configuration for the application.

    Args:
        level: Logging level (e.g., logging.INFO). If None, uses INFO by default.
    """
    if level is None:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set external library loggers to WARNING to reduce noise
    # google-genai library logs INFO messages for HTTP requests and AFC status
    # Try multiple possible logger names used by the library
    for logger_name in [
        "google.genai",
        "google-genai",
        "google.generativeai",
        "google",
        "genai",
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Also add a filter to suppress INFO messages from google-genai and HTTP libraries
    # The HTTP Request messages might come from urllib3, httpx, or google-genai itself
    class SuppressExternalInfoFilter(logging.Filter):
        """Filter to suppress INFO messages from external libraries."""

        def filter(self, record: logging.LogRecord) -> bool:  # noqa: PLR6301
            """Filter out INFO messages from external libraries."""
            # Suppress INFO messages from google.* loggers
            if record.name.startswith("google") and record.levelno == logging.INFO:
                return False
            # Suppress INFO messages from HTTP libraries (urllib3, httpx, requests)
            if (
                record.name.startswith(("urllib3", "httpx", "httpcore", "requests"))
                and record.levelno == logging.INFO
            ):
                return False
            # Suppress INFO messages containing "HTTP Request" (catch-all)
            return not (
                record.levelno == logging.INFO and "HTTP Request" in record.getMessage()
            )

    # Apply the filter to all handlers
    for handler in logging.root.handlers:
        handler.addFilter(SuppressExternalInfoFilter())
