"""Step definitions for file size limits feature."""

import os
import pathlib

from behave import given, then

# Reuse common steps from git_commit_review_steps

# Default size limit: 1MB (can be configured)
DEFAULT_SIZE_LIMIT = 1024 * 1024  # 1MB in bytes

# Note: Many steps are reused from git_commit_review_steps.py and config_rules_steps.py
# Only file-size-specific steps are defined here


@given("I have staged a file larger than the size limit")
def step_given_staged_large_file(context):
    """Create and stage a file that exceeds the size limit."""
    # Create a file larger than 1MB
    test_file = os.path.join(context.temp_dir, "large_file.py")
    # Create content larger than 1MB (1MB + 1KB to be sure)
    large_content = "# " + "x" * (DEFAULT_SIZE_LIMIT + 1024)
    pathlib.Path(test_file).write_text(large_content, encoding="utf-8")

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]
    context.large_files = [test_file]


@given("I have staged a file smaller than the size limit")
def step_given_staged_small_file(context):
    """Create and stage a file that is within the size limit."""
    test_file = os.path.join(context.temp_dir, "small_file.py")
    # Create a small file with good code
    small_content = """\"\"\"A small Python file.\"\"\"

def hello() -> str:
    \"\"\"Return a greeting.

    Returns:
        A greeting string.
    \"\"\"
    return "Hello, World!"
"""
    pathlib.Path(test_file).write_text(small_content, encoding="utf-8")

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]
    context.small_files = [test_file]


@given("I have staged both large and small files")
def step_given_staged_mixed_files(context):
    """Create and stage both large and small files."""
    # Large file
    large_file = os.path.join(context.temp_dir, "large_file.py")
    large_content = "# " + "x" * (DEFAULT_SIZE_LIMIT + 1024)
    pathlib.Path(large_file).write_text(large_content, encoding="utf-8")
    context.git_repo.index.add([large_file])

    # Small file
    small_file = os.path.join(context.temp_dir, "small_file.py")
    small_content = """def func() -> int:
    return 42
"""
    pathlib.Path(small_file).write_text(small_content, encoding="utf-8")
    context.git_repo.index.add([small_file])

    context.staged_files = [large_file, small_file]
    context.large_files = [large_file]
    context.small_files = [small_file]


@given("I have staged only files larger than the size limit")
def step_given_staged_only_large_files(context):
    """Create and stage only files that exceed the size limit."""
    large_file1 = os.path.join(context.temp_dir, "large_file1.py")
    large_file2 = os.path.join(context.temp_dir, "large_file2.py")

    large_content = "# " + "x" * (DEFAULT_SIZE_LIMIT + 1024)

    pathlib.Path(large_file1).write_text(large_content, encoding="utf-8")
    pathlib.Path(large_file2).write_text(large_content, encoding="utf-8")

    context.git_repo.index.add([large_file1, large_file2])
    context.staged_files = [large_file1, large_file2]
    context.large_files = [large_file1, large_file2]


# All common steps (when, then for pre-commit check) are reused from other step files
# Only file-size-specific steps are defined below


@then("the large file should be skipped from review")
def step_then_large_file_skipped(context):
    """Verify that large files were skipped."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "large_files")

    feedback_lower = context.hook_feedback.lower()
    for large_file in context.large_files:
        file_name = os.path.basename(large_file)
        # The file should not appear in the review feedback
        # Or if it does, it should mention being skipped
        assert (
            file_name.lower() not in feedback_lower
            or "skip" in feedback_lower
            or "too large" in feedback_lower
            or "size limit" in feedback_lower
        ), f"Large file {file_name} should be skipped but appears in feedback"


@then("large files should be skipped")
def step_then_large_files_skipped(context):
    """Verify that all large files were skipped."""
    assert hasattr(context, "large_files")
    feedback_lower = context.hook_feedback.lower()

    for large_file in context.large_files:
        file_name = os.path.basename(large_file)
        # Large files should not appear in review or should be marked as skipped
        assert (
            file_name.lower() not in feedback_lower
            or "skip" in feedback_lower
            or "too large" in feedback_lower
        ), f"Large file {file_name} should be skipped"


@then("the file should be reviewed")
def step_then_file_reviewed(context):
    """Verify that the file was reviewed."""
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None
    # If file was reviewed, we should have feedback
    assert hasattr(context, "hook_feedback")
    assert context.hook_feedback is not None
    assert len(context.hook_feedback.strip()) > 0


@then("small files should be reviewed")
def step_then_small_files_reviewed(context):
    """Verify that small files were reviewed."""
    assert hasattr(context, "small_files")
    assert hasattr(context, "hook_result")
    # Small files should be included in the review
    assert context.hook_result is not None


@then("all files should be skipped")
def step_then_all_files_skipped(context):
    """Verify that all files were skipped."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "large_files")
    # If all files are skipped, we should get a message about it
    feedback_lower = context.hook_feedback.lower()
    assert (
        "skip" in feedback_lower
        or "too large" in feedback_lower
        or "size limit" in feedback_lower
        or "no files" in feedback_lower
    ), "Should indicate that files were skipped due to size"


# All other steps are reused from git_commit_review_steps.py and config_rules_steps.py


@then("I should receive a message indicating the file was skipped")
def step_then_receive_skip_message(context):
    """Verify that a skip message was received."""
    assert hasattr(context, "hook_feedback")
    feedback_lower = context.hook_feedback.lower()
    # Should mention skipping or size limit
    assert any(
        keyword in feedback_lower
        for keyword in ["skip", "too large", "size limit", "exceed"]
    ), "Should indicate file was skipped due to size"


@then("I should receive a message indicating all files were skipped")
def step_then_receive_all_skipped_message(context):
    """Verify that a message indicating all files were skipped."""
    assert hasattr(context, "hook_feedback")
    feedback_lower = context.hook_feedback.lower()
    # Should mention that all files were skipped
    assert any(
        keyword in feedback_lower
        for keyword in [
            "skip",
            "too large",
            "size limit",
            "all files",
            "no files to review",
        ]
    ), "Should indicate all files were skipped"
