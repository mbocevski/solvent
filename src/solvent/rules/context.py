"""Context rules handling for .solventrules files."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from pathspec import PathSpec

logger = logging.getLogger(__name__)

SOLVENTRULES_FILENAME = ".solventrules"

# Pattern to match rule sections: [pattern]
RULE_SECTION_PATTERN = re.compile(r"^\[(.+)\]$")
# Pattern to match context line: context = value
CONTEXT_PATTERN = re.compile(r"^context\s*=\s*(.+)$", re.IGNORECASE)


@dataclass
class ContextRule:
    """A context rule that applies to files matching a pattern.

    Attributes:
        pattern: File pattern to match (gitignore-style).
        context: Context string to provide to the AI for matching files.
    """

    pattern: str
    context: str
    _spec: PathSpec | None = None

    def __post_init__(self) -> None:
        """Initialize the PathSpec for pattern matching."""
        try:
            self._spec = PathSpec.from_lines("gitwildmatch", [self.pattern])
        except Exception as e:
            logger.warning(f"Invalid pattern in context rule '{self.pattern}': {e}")
            self._spec = None

    def matches(self, file_path: str) -> bool:
        """Check if a file path matches this rule's pattern.

        Args:
            file_path: File path to check (relative to repo root).

        Returns:
            True if the file path matches the pattern.
        """
        if self._spec is None:
            return False

        return self._spec.match_file(file_path)


def load_context_rules(repo_path: str | Path) -> list[ContextRule]:
    """Load context rules from .solventrules file.

    Args:
        repo_path: Path to the git repository root.

    Returns:
        List of ContextRule objects, empty list if file doesn't exist or is invalid.
    """
    repo_path = Path(repo_path)
    solventrules_path = repo_path / SOLVENTRULES_FILENAME

    if not solventrules_path.exists():
        logger.debug(f"No {SOLVENTRULES_FILENAME} file found at {solventrules_path}")
        return []

    try:
        content = solventrules_path.read_text(encoding="utf-8")
        rules = _parse_rules_file(content)
        logger.debug(
            f"Loaded {len(rules)} context rule(s) from {SOLVENTRULES_FILENAME}"
        )
    except Exception as e:
        logger.warning(f"Error loading {SOLVENTRULES_FILENAME}: {e}")
        return []
    else:
        return rules


def _parse_rules_file(content: str) -> list[ContextRule]:
    """Parse the content of a .solventrules file.

    Args:
        content: File content as string.

    Returns:
        List of ContextRule objects parsed from the content.
    """
    rules = []
    lines = content.splitlines()
    current_pattern = None
    current_context_parts = []

    for line_raw in lines:
        line = line_raw.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Check for pattern section: [pattern]
        section_match = RULE_SECTION_PATTERN.match(line)
        if section_match:
            # Save previous rule if we have one
            if current_pattern and current_context_parts:
                context = "\n".join(current_context_parts).strip()
                if context:
                    rules.append(ContextRule(pattern=current_pattern, context=context))

            # Start new rule
            current_pattern = section_match.group(1)
            current_context_parts = []
            continue

        # Check for context line: context = value
        context_match = CONTEXT_PATTERN.match(line)
        if context_match:
            if current_pattern:
                context_value = context_match.group(1).strip()
                current_context_parts.append(context_value)
            else:
                logger.warning(f"Context line found without pattern section: {line}")
            continue

        # If we're in a context block (have a pattern), treat as continuation
        if current_pattern:
            current_context_parts.append(line)

    # Save last rule
    if current_pattern and current_context_parts:
        context = "\n".join(current_context_parts).strip()
        if context:
            rules.append(ContextRule(pattern=current_pattern, context=context))

    return rules


def get_context_for_file(file_path: str, rules: list[ContextRule]) -> str | None:
    """Get context string for a file based on matching rules.

    Args:
        file_path: File path to get context for (relative to repo root).
        rules: List of ContextRule objects to check.

    Returns:
        Context string if a matching rule is found, None otherwise.
    """
    # Check rules in order - first match wins
    for rule in rules:
        if rule.matches(file_path):
            logger.debug(f"File {file_path} matches rule pattern: {rule.pattern}")
            return rule.context

    return None
