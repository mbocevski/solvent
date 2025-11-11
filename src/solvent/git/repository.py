"""Git repository operations."""

import logging
from pathlib import Path

from git import Repo

from solvent.config.settings import get_settings
from solvent.models.file_info import FileInfo

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

    Files that cannot be read (binary, encoding errors, too large, etc.) are
    skipped and logged, but not included in the returned dictionary to avoid
    confusing the AI with error messages that might be interpreted as code.

    Args:
        repo: Git repository.
        file_paths: List of file paths to read.

    Returns:
        Dictionary mapping file paths to their contents. Only includes files
        that were successfully read and are within size limits.
    """
    file_contents = {}
    repo_root = Path(repo.working_dir)
    skipped_files = []
    settings = get_settings()
    max_size = settings.max_file_size

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

            # Check file size before reading
            file_size = full_path.stat().st_size
            if file_size > max_size:
                size_mb = file_size / (1024 * 1024)
                max_mb = max_size / (1024 * 1024)
                logger.info(
                    f"File {file_path} is too large "
                    f"({size_mb:.2f}MB > {max_mb:.2f}MB), skipping from review"
                )
                skipped_files.append(
                    (file_path, f"File too large ({size_mb:.2f}MB > {max_mb:.2f}MB)")
                )
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


def get_staged_file_info(  # noqa: PLR0912, PLR0915, PLR0914
    repo: Repo, file_paths: list[str]
) -> dict[str, FileInfo]:
    """Get diff and file information for staged files.

    For each staged file, determines if it's new, modified, or deleted, and
    retrieves the appropriate diff and original content.

    Args:
        repo: Git repository.
        file_paths: List of file paths to analyze.

    Returns:
        Dictionary mapping file paths to FileInfo objects. Only includes files
        that were successfully processed and are within size limits.
    """
    file_info_dict = {}
    repo_root = Path(repo.working_dir)
    skipped_files = []
    settings = get_settings()
    max_size = settings.max_file_size

    # Check if we have any commits (to determine if file is new or modified)
    try:
        # Try to access HEAD - if it exists, we have commits
        _ = repo.head.commit
        has_commits = True
    except (ValueError, AttributeError):
        # No HEAD means no commits yet
        has_commits = False

    for file_path in file_paths:
        full_path = repo_root / file_path
        file_type = None
        diff = None
        original_content = None
        new_content = None

        try:
            # Check if file exists in working directory
            file_exists = full_path.exists() and full_path.is_file()

            # Check if file exists in HEAD (for modified/deleted detection)
            exists_in_head = False
            if has_commits:
                try:
                    # Try to get file from HEAD
                    head_file = repo.head.commit.tree / file_path
                    exists_in_head = True
                    # Try to read original content (might be binary)
                    try:
                        original_content = head_file.data_stream.read().decode("utf-8")
                    except (UnicodeDecodeError, AttributeError):
                        # Binary file or can't decode - skip
                        logger.debug(
                            f"File {file_path} in HEAD is binary or unreadable, "
                            "treating as new file"
                        )
                        exists_in_head = False
                except (KeyError, AttributeError):
                    # File doesn't exist in HEAD
                    exists_in_head = False

            # Determine file type
            if not exists_in_head and file_exists:
                file_type = "new"
            elif exists_in_head and file_exists:
                file_type = "modified"
            elif exists_in_head and not file_exists:
                file_type = "deleted"
            else:
                # Edge case: file doesn't exist and wasn't in HEAD
                logger.warning(
                    f"File {file_path} doesn't exist and wasn't in HEAD, skipping"
                )
                skipped_files.append((file_path, "File doesn't exist"))
                continue

            # Get diff for modified files
            if file_type == "modified" and has_commits:
                try:
                    # Compare staged (index) to HEAD - shows what changed
                    diff = repo.git.diff("--cached", "--", file_path)
                    if not diff.strip():
                        # No diff means file wasn't actually changed, skip
                        logger.debug(f"File {file_path} has no changes, skipping")
                        continue
                except Exception as e:
                    logger.warning(f"Error getting diff for {file_path}: {e}")
                    # Fallback to full content
                    diff = None

            # Get diff for deleted files
            if file_type == "deleted" and has_commits:
                try:
                    # Compare staged (index) to HEAD - shows what was deleted
                    diff = repo.git.diff("--cached", "--", file_path)
                except Exception as e:
                    logger.warning(f"Error getting diff for deleted {file_path}: {e}")

            # Read new content for new and modified files
            if file_type in {"new", "modified"} and file_exists:
                # Check file size before reading
                file_size = full_path.stat().st_size
                if file_size > max_size:
                    size_mb = file_size / (1024 * 1024)
                    max_mb = max_size / (1024 * 1024)
                    logger.info(
                        f"File {file_path} is too large "
                        f"({size_mb:.2f}MB > {max_mb:.2f}MB), skipping from review"
                    )
                    skipped_files.append(
                        (
                            file_path,
                            f"File too large ({size_mb:.2f}MB > {max_mb:.2f}MB)",
                        )
                    )
                    continue

                new_content = full_path.read_text(encoding="utf-8")

            # For new files without commits, we can't get a diff
            if file_type == "new" and not has_commits:
                diff = None

            file_info_dict[file_path] = FileInfo(
                path=file_path,
                diff=diff,
                original_content=original_content,
                new_content=new_content,
                file_type=file_type,
            )

        except UnicodeDecodeError:
            logger.warning(
                f"File {file_path} is not UTF-8 encoded, skipping from review"
            )
            skipped_files.append((file_path, "Not UTF-8 encoded (binary file)"))
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {e}")
            skipped_files.append((file_path, f"Processing error: {e}"))

    if skipped_files:
        logger.info(
            f"Skipped {len(skipped_files)} file(s) that could not be processed: "
            f"{', '.join(f'{path} ({reason})' for path, reason in skipped_files)}"
        )

    return file_info_dict
