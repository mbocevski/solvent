"""Ignore pattern handling for .solventignore files."""

import logging
from pathlib import Path

from pathspec import PathSpec

logger = logging.getLogger(__name__)

SOLVENTIGNORE_FILENAME = ".solventignore"


def load_ignore_patterns(repo_path: str | Path) -> PathSpec | None:
    """Load ignore patterns from .solventignore file.

    Args:
        repo_path: Path to the git repository root.

    Returns:
        PathSpec object with ignore patterns, or None if .solventignore doesn't exist.
    """
    repo_path = Path(repo_path)
    solventignore_path = repo_path / SOLVENTIGNORE_FILENAME

    if not solventignore_path.exists():
        logger.debug(f"No {SOLVENTIGNORE_FILENAME} file found at {solventignore_path}")
        return None

    try:
        patterns = solventignore_path.read_text(encoding="utf-8").splitlines()
        # Filter out empty lines and comments
        patterns = [
            line.strip()
            for line in patterns
            if line.strip() and not line.strip().startswith("#")
        ]

        if not patterns:
            logger.debug(
                f"{SOLVENTIGNORE_FILENAME} file is empty or contains only comments"
            )
            return None

        spec = PathSpec.from_lines("gitwildmatch", patterns)
        logger.debug(
            f"Loaded {len(patterns)} ignore pattern(s) from {SOLVENTIGNORE_FILENAME}"
        )
    except Exception as e:
        logger.warning(f"Error loading {SOLVENTIGNORE_FILENAME}: {e}")
        return None
    else:
        return spec


def filter_ignored_files(
    file_paths: list[str], ignore_spec: PathSpec | None, repo_path: str | Path
) -> list[str]:
    """Filter out files that match ignore patterns.

    Args:
        file_paths: List of file paths to filter (relative to repo root).
        ignore_spec: PathSpec with ignore patterns, or None if no ignore file.
        repo_path: Path to the git repository root.

    Returns:
        List of file paths that should not be ignored.
    """
    if ignore_spec is None:
        logger.debug("No ignore patterns to apply")
        return file_paths

    repo_path = Path(repo_path)
    filtered = []

    for file_path in file_paths:
        # PathSpec expects paths relative to the repo root
        # Check if the file matches any ignore pattern
        if ignore_spec.match_file(file_path):
            logger.debug(f"Ignoring file matching pattern: {file_path}")
        else:
            filtered.append(file_path)

    if len(filtered) < len(file_paths):
        logger.debug(
            f"Filtered {len(file_paths) - len(filtered)} file(s) "
            f"using {SOLVENTIGNORE_FILENAME} patterns"
        )

    return filtered
