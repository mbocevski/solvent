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
    logging.getLogger("google.genai").setLevel(logging.WARNING)
