"""Git repository operations."""

import logging
from pathlib import Path

from git import Repo

logger = logging.getLogger(__name__)


def get_staged_files(repo: Repo) -> list[str]:
    """Get list of staged file paths.

    Args:
        repo: Git repository.

    Returns:
        List of file paths that are staged.
    """
    staged_files = set()

    try:
        # Use git diff --cached to get staged files (works even with no commits)
        # This is more reliable than index.entries for new repositories
        staged_output = repo.git.diff("--cached", "--name-only", "--diff-filter=AM")
        if staged_output:
            for file_path in staged_output.split("\n"):
                stripped_path = file_path.strip()
                if stripped_path:
                    staged_files.add(stripped_path)
    except Exception as e:
        logger.warning(f"Error getting staged files via git diff: {e}")
        # Fallback to index.entries method
        # GitPython index.entries returns tuples: (mode, hexsha, stage, path)
        try:
            for entry in repo.index.entries:
                # Type check: entry should be a tuple with at least 4 elements
                if not isinstance(entry, tuple) or len(entry) < 4:
                    logger.warning(f"Unexpected index entry format: {entry}, skipping")
                    continue

                # Extract path from tuple: (mode, hexsha, stage, path)
                file_path = entry[3]

                # Verify it's a file (not a directory)
                full_path = Path(repo.working_dir) / file_path
                if full_path.exists() and full_path.is_file():
                    staged_files.add(file_path)
        except Exception as fallback_error:
            logger.error(
                f"Error getting staged files via index.entries: {fallback_error}"
            )

    return sorted(staged_files)


def read_staged_files(repo: Repo, file_paths: list[str]) -> dict[str, str]:
    """Read contents of staged files.

    Files that cannot be read (binary, encoding errors, etc.) are skipped and
    logged, but not included in the returned dictionary to avoid confusing
    the AI with error messages that might be interpreted as code.

    Args:
        repo: Git repository.
        file_paths: List of file paths to read.

    Returns:
        Dictionary mapping file paths to their contents. Only includes files
        that were successfully read.
    """
    file_contents = {}
    repo_root = Path(repo.working_dir)
    skipped_files = []

    for file_path in file_paths:
        full_path = repo_root / file_path
        try:
            if not full_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                skipped_files.append((file_path, "File does not exist"))
                continue

            if not full_path.is_file():
                logger.debug(f"Skipping non-file: {file_path}")
                skipped_files.append((file_path, "Not a file"))
                continue

            content = full_path.read_text(encoding="utf-8")
            file_contents[file_path] = content
        except UnicodeDecodeError:
            logger.warning(
                f"File {file_path} is not UTF-8 encoded, skipping from review"
            )
            skipped_files.append((file_path, "Not UTF-8 encoded (binary file)"))
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            skipped_files.append((file_path, f"Read error: {e}"))

    if skipped_files:
        logger.info(
            f"Skipped {len(skipped_files)} file(s) that could not be read: "
            f"{', '.join(f'{path} ({reason})' for path, reason in skipped_files)}"
        )

    return file_contents
