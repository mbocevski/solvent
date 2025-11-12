"""Pre-commit hook orchestration for reviewing staged files."""

import logging
from pathlib import Path

from git import Repo

from solvent_ai.ai import GeminiClient
from solvent_ai.git import get_staged_file_info, get_staged_files
from solvent_ai.hook.evaluator import should_block_commit
from solvent_ai.models.hook import HookResult
from solvent_ai.rules import (
    filter_ignored_files,
    load_context_rules,
    load_ignore_patterns,
)

logger = logging.getLogger(__name__)


def run_pre_commit_review(repo_path: str | None = None) -> HookResult:
    """Run pre-commit review on staged files.

    Args:
        repo_path: Path to the git repository. If None, uses current directory.

    Returns:
        HookResult with passed status and feedback.
    """
    if repo_path is None:
        repo_path = "."

    try:
        repo = Repo(repo_path)
    except Exception as e:
        logger.error(f"Error accessing git repository at {repo_path}: {e}")
        return HookResult(
            passed=False,
            feedback=f"Error accessing git repository: {e}. Pre-commit check failed.",
        )

    staged_files = get_staged_files(repo)

    if not staged_files:
        logger.info("No staged files to review")
        return HookResult(
            passed=True, feedback="No staged files to review. Pre-commit check passed."
        )

    # Load and apply ignore patterns
    repo_root = Path(repo.working_dir)
    ignore_spec = load_ignore_patterns(repo_root)
    filtered_files = filter_ignored_files(staged_files, ignore_spec, repo_root)

    if not filtered_files:
        logger.info("All staged files are ignored by .solventignore patterns")
        return HookResult(
            passed=True,
            feedback="All staged files are ignored. Pre-commit check passed.",
        )

    logger.debug(
        f"Reviewing {len(filtered_files)} staged file(s) "
        f"(filtered from {len(staged_files)} total): {', '.join(filtered_files)}"
    )

    # Load context rules
    context_rules = load_context_rules(repo_root)

    # Get file info with diffs (files that are too large will be skipped)
    file_info_dict = get_staged_file_info(repo, filtered_files)

    if not file_info_dict:
        # Check if all files were skipped due to size
        # If we had filtered files but none were readable, they might all be too large
        logger.info(
            "No file contents could be read. All files may be too large or unreadable."
        )
        return HookResult(
            passed=True,
            feedback=(
                "All staged files were skipped (too large, binary, or unreadable). "
                "Pre-commit check passed."
            ),
        )

    # Review with AI
    try:
        client = GeminiClient()
        feedback = client.review_staged_files(file_info_dict, context_rules)
    except Exception as e:
        error_str = str(e)
        # Provide user-friendly error messages
        if "503" in error_str or "UNAVAILABLE" in error_str:
            user_message = (
                "AI review service is temporarily unavailable. "
                "Please try again in a moment."
            )
        elif "429" in error_str or "RATE_LIMIT" in error_str or "QUOTA" in error_str:
            user_message = (
                "AI review service rate limit exceeded. Please try again in a moment."
            )
        elif "401" in error_str or "UNAUTHENTICATED" in error_str:
            user_message = (
                "AI review authentication failed. "
                "Please check your API key configuration."
            )
        elif "403" in error_str or "PERMISSION_DENIED" in error_str:
            user_message = (
                "AI review permission denied. Please check your API key permissions."
            )
        else:
            user_message = f"AI review service error: {error_str}"

        logger.error(f"Error during AI review: {e}")
        return HookResult(
            passed=False,
            feedback=f"{user_message} Pre-commit check failed.",
        )

    # Determine if hook should pass or fail
    should_block = should_block_commit(feedback)
    passed = not should_block

    return HookResult(passed=passed, feedback=feedback)
