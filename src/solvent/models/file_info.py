"""Data models for file information in reviews."""

from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file for AI review.

    Attributes:
        path: File path relative to repository root.
        diff: Git diff showing changes (None for new files).
        original_content: Original file content from HEAD (None for new files).
        new_content: New file content (None for deleted files).
        file_type: Type of change: 'new', 'modified', or 'deleted'.
    """

    path: str
    diff: str | None
    original_content: str | None
    new_content: str | None
    file_type: str  # 'new', 'modified', or 'deleted'
