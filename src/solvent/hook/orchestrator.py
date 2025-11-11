"""Pre-commit hook orchestration for reviewing staged files."""

import logging

from git import Repo

from solvent.ai import GeminiClient
from solvent.git import get_staged_files, read_staged_files
from solvent.hook.evaluator import should_block_commit
from solvent.models.hook import HookResult

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

    logger.info(
        f"Reviewing {len(staged_files)} staged file(s): {', '.join(staged_files)}"
    )

    # Get file contents
    file_contents = read_staged_files(repo, staged_files)

    if not file_contents:
        logger.warning("No file contents could be read")
        return HookResult(
            passed=False,
            feedback="Unable to read staged files. Pre-commit check failed.",
        )

    # Review with AI
    try:
        client = GeminiClient()
        feedback = client.review_staged_files(file_contents)
    except Exception as e:
        logger.error(f"Error during AI review: {e}")
        return HookResult(
            passed=False,
            feedback=f"Error during AI review: {e}. Pre-commit check failed.",
        )

    # Determine if hook should pass or fail
    should_block = should_block_commit(feedback)
    passed = not should_block

    return HookResult(passed=passed, feedback=feedback)
