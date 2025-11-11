"""Retry logic for transient API errors."""

import logging
import random
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Maximum number of retry attempts (including initial attempt)
MAX_RETRIES = 3

# Base delay in seconds for exponential backoff
BASE_DELAY = 1.0

# Maximum delay in seconds
MAX_DELAY = 4.0


def is_transient_error(error: Exception) -> bool:  # noqa: PLR0911
    """Check if an error is transient and should be retried.

    Args:
        error: The exception to check.

    Returns:
        True if the error is transient and should be retried, False otherwise.
    """
    error_str = str(error).upper()
    error_type = type(error).__name__

    # Check for HTTP status codes in error message
    if "503" in error_str or "UNAVAILABLE" in error_str:
        return True  # Service unavailable
    if "429" in error_str or "RATE_LIMIT" in error_str or "QUOTA" in error_str:
        return True  # Rate limiting
    if "500" in error_str or "INTERNAL" in error_str:
        return True  # Internal server error
    if "502" in error_str or "BAD_GATEWAY" in error_str:
        return True  # Bad gateway
    if "504" in error_str or "GATEWAY_TIMEOUT" in error_str:
        return True  # Gateway timeout

    # Check for network-related errors
    if any(
        keyword in error_type or keyword in error_str
        for keyword in [
            "Timeout",
            "Connection",
            "Network",
            "Socket",
            "Temporary",
            "Transient",
        ]
    ):
        return True

    # Permanent errors that should NOT be retried
    permanent_keywords = [
        "400",
        "401",
        "403",
        "404",
        "UNAUTHENTICATED",
        "PERMISSION_DENIED",
        "NOT_FOUND",
        "INVALID_ARGUMENT",
    ]
    # Default: treat unknown errors as transient (conservative approach)
    # This allows retries for unexpected errors that might be transient
    return not any(keyword in error_str for keyword in permanent_keywords)


def retry_with_backoff(
    func: Callable[[], T],
    operation_name: str = "operation",
    max_retries: int = MAX_RETRIES,
) -> T:
    """Retry a function with exponential backoff for transient errors.

    Args:
        func: The function to retry (should be a callable with no arguments).
        operation_name: Name of the operation for logging purposes.
        max_retries: Maximum number of retry attempts (including initial attempt).

    Returns:
        The result of the function call.

    Raises:
        Exception: The last exception raised if all retries are exhausted.
        RuntimeError: If retries are exhausted without a valid exception.
    """
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e

            # Check if this is a transient error that should be retried
            if not is_transient_error(e):
                logger.debug(
                    f"{operation_name} failed with permanent error (not retrying): {e}"
                )
                raise

            # If this is the last attempt, don't wait, just raise
            if attempt >= max_retries:
                logger.warning(
                    f"{operation_name} failed after {max_retries} attempts: {e}"
                )
                raise

            # Calculate exponential backoff with jitter
            delay = min(BASE_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
            # Add jitter (random 0-20% of delay) to avoid thundering herd
            jitter = delay * 0.2 * random.random()
            total_delay = delay + jitter

            logger.debug(
                f"{operation_name} failed (attempt {attempt}/{max_retries}): {e}. "
                f"Retrying in {total_delay:.2f}s..."
            )

            time.sleep(total_delay)

    # This should never be reached, but just in case
    if last_exception:
        raise last_exception

    raise RuntimeError(f"{operation_name} failed after {max_retries} attempts")
