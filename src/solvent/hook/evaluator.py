"""Evaluation logic for determining if pre-commit hook should pass or fail."""

import logging
import re

logger = logging.getLogger(__name__)

# Pattern to match the machine-readable status block
STATUS_BLOCK_PATTERN = re.compile(
    r"---BEGIN STATUS---\s*"
    r"STATUS:\s*(PASS|FAIL)\s*"
    r"CRITICAL_ISSUES_COUNT:\s*(\d+)\s*"
    r"---END STATUS---",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


def should_block_commit(feedback: str) -> bool:
    """Determine if pre-commit hook should block the commit based on feedback.

    First attempts to parse the machine-readable status block. If not found,
    falls back to keyword-based detection.

    Args:
        feedback: AI-generated feedback.

    Returns:
        True if commit should be blocked, False if it should pass.
    """
    # Try to parse the machine-readable status block
    status_match = STATUS_BLOCK_PATTERN.search(feedback)
    if status_match:
        status = status_match.group(1).upper()
        critical_count = int(status_match.group(2))

        logger.debug(
            f"Parsed status block: STATUS={status}, "
            f"CRITICAL_ISSUES_COUNT={critical_count}"
        )

        if status == "FAIL" or critical_count > 0:
            logger.warning(
                f"Commit should be blocked: STATUS={status}, "
                f"critical issues={critical_count}"
            )
            return True

        logger.debug("Status block indicates commit should pass")
        return False

    # Fallback to keyword-based detection if status block not found
    logger.warning(
        "Machine-readable status block not found, falling back to keyword detection"
    )
    return _should_block_commit_keyword_fallback(feedback)


def _should_block_commit_keyword_fallback(feedback: str) -> bool:
    """Fallback keyword-based detection for determining if commit should be blocked.

    Args:
        feedback: AI-generated feedback.

    Returns:
        True if commit should be blocked, False if it should pass.
    """
    feedback_lower = feedback.lower()

    # Critical issues that should cause failure
    # These keywords indicate serious problems that must be fixed
    critical_keywords = [
        "security vulnerability",
        "security risk",
        "critical error",
        "dangerous",
        "unsafe",
        "vulnerability",
        "exploit",
        "injection",
        "xss",
        "sql injection",
        "code injection",
        "remote code execution",
        "must fix",
        "blocking issue",
        "severe",
        "critical",
        "should block",
        "must not commit",
    ]

    # Check for critical issues
    for keyword in critical_keywords:
        if keyword in feedback_lower:
            logger.warning(f"Found critical issue keyword: {keyword}")
            return True

    # If no critical issues, pass (even with suggestions)
    logger.info("No critical issues found, pre-commit check passes")
    return False
