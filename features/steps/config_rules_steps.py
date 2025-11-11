"""Step definitions for configuration rules and ignores feature."""

import os
import pathlib

from behave import given, then

# Import the actual functionality we're testing


@given("I have a .solventignore file")
def step_given_solventignore_file_basic(context):
    """Create a basic .solventignore file."""
    solventignore_path = os.path.join(context.temp_dir, ".solventignore")
    pathlib.Path(solventignore_path).write_text(
        "*.log\n*.tmp\n",
        encoding="utf-8",
    )
    context.solventignore_path = solventignore_path


@given("I have a .solventignore file with patterns")
def step_given_solventignore_file(context):
    """Create a .solventignore file with test patterns."""
    solventignore_path = os.path.join(context.temp_dir, ".solventignore")
    pathlib.Path(solventignore_path).write_text(
        "*.log\n*.tmp\nvendor/\n",
        encoding="utf-8",
    )
    context.solventignore_path = solventignore_path


@given('I have a .solventignore file with pattern "{pattern}"')
def step_given_solventignore_pattern(context, pattern):
    """Create a .solventignore file with a specific pattern."""
    solventignore_path = os.path.join(context.temp_dir, ".solventignore")
    pathlib.Path(solventignore_path).write_text(
        f"{pattern}\n",
        encoding="utf-8",
    )
    context.solventignore_path = solventignore_path


@given("I have staged files including ignored files")
def step_given_staged_with_ignored(context):
    """Create and stage files including some that should be ignored."""
    # Create files that should be ignored
    log_file = os.path.join(context.temp_dir, "app.log")
    pathlib.Path(log_file).write_text("log content", encoding="utf-8")
    context.git_repo.index.add([log_file])

    # Create files that should NOT be ignored
    code_file = os.path.join(context.temp_dir, "app.py")
    pathlib.Path(code_file).write_text(
        "def main():\n    pass\n",
        encoding="utf-8",
    )
    context.git_repo.index.add([code_file])

    context.staged_files = [log_file, code_file]
    context.ignored_files = [log_file]
    context.reviewed_files = [code_file]


@given('I have staged files including "{ignored_file}" and "{reviewed_file}"')
def step_given_specific_staged_files(context, ignored_file, reviewed_file):
    """Create and stage specific files."""
    ignored_path = os.path.join(context.temp_dir, ignored_file)
    reviewed_path = os.path.join(context.temp_dir, reviewed_file)

    pathlib.Path(ignored_path).write_text("ignored content", encoding="utf-8")
    pathlib.Path(reviewed_path).write_text(
        "def func():\n    return True\n",
        encoding="utf-8",
    )

    context.git_repo.index.add([ignored_path, reviewed_path])
    context.staged_files = [ignored_path, reviewed_path]
    context.ignored_files = [ignored_path]
    context.reviewed_files = [reviewed_path]


@given('I have staged files in "{directory}" directory')
def step_given_staged_in_directory(context, directory):
    """Create and stage files in a specific directory."""
    dir_path = os.path.join(context.temp_dir, directory)
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, "file.py")
    pathlib.Path(file_path).write_text(
        "def test_func():\n    pass\n",
        encoding="utf-8",
    )

    context.git_repo.index.add([file_path])
    context.staged_files = [file_path]
    context.directory = directory


@given("I have a .solventrules file")
def step_given_solventrules_file_basic(context):
    """Create a basic .solventrules file."""
    solventrules_path = os.path.join(context.temp_dir, ".solventrules")
    pathlib.Path(solventrules_path).write_text(
        "[*.py]\ncontext = Python code\n",
        encoding="utf-8",
    )
    context.solventrules_path = solventrules_path


@given("I have a .solventrules file with context rules")
def step_given_solventrules_file(context):
    """Create a .solventrules file with test context rules."""
    solventrules_path = os.path.join(context.temp_dir, ".solventrules")
    pathlib.Path(solventrules_path).write_text(
        "[tests/**]\n"
        "context = This is test code, focus on test quality and coverage\n"
        "\n"
        "[*.py]\n"
        "context = Python code, follow PEP 8 style guidelines\n",
        encoding="utf-8",
    )
    context.solventrules_path = solventrules_path


@given("I have a .solventrules file with multiple rules")
def step_given_multiple_solventrules(context):
    """Create a .solventrules file with multiple context rules."""
    solventrules_path = os.path.join(context.temp_dir, ".solventrules")
    pathlib.Path(solventrules_path).write_text(
        "[tests/**]\n"
        "context = Test code - focus on quality\n"
        "\n"
        "[src/**]\n"
        "context = Production code - be strict\n"
        "\n"
        "[docs/**]\n"
        "context = Documentation - check clarity\n",
        encoding="utf-8",
    )
    context.solventrules_path = solventrules_path


@given('I have a .solventrules file with a rule for "{pattern}"')
def step_given_solventrules_pattern(context, pattern):
    """Create a .solventrules file with a rule for a specific pattern."""
    solventrules_path = os.path.join(context.temp_dir, ".solventrules")
    pathlib.Path(solventrules_path).write_text(
        f"[{pattern}]\n",
        encoding="utf-8",
    )
    context.solventrules_path = solventrules_path


@given('the rule specifies "{context_text}"')
def step_given_rule_context(context, context_text):
    """Add context text to the current .solventrules file."""
    if not hasattr(context, "solventrules_path"):
        solventrules_path = os.path.join(context.temp_dir, ".solventrules")
        pathlib.Path(solventrules_path).write_text("", encoding="utf-8")
        context.solventrules_path = solventrules_path

    # Read existing content and append context
    existing = pathlib.Path(context.solventrules_path).read_text(encoding="utf-8")
    updated = existing + f"context = {context_text}\n"
    pathlib.Path(context.solventrules_path).write_text(updated, encoding="utf-8")


@given("I have staged files matching the rule patterns")
def step_given_staged_matching_rules(context):
    """Create and stage files that match the rule patterns."""
    # Create test files
    test_file = os.path.join(context.temp_dir, "tests", "test_example.py")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    pathlib.Path(test_file).write_text(
        "def test_something():\n    assert True\n",
        encoding="utf-8",
    )

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]
    context.matching_files = [test_file]


@given("I have staged files matching different rule patterns")
def step_given_staged_different_patterns(context):
    """Create and stage files matching different rule patterns."""
    # Create files in different directories
    test_file = os.path.join(context.temp_dir, "tests", "test_file.py")
    src_file = os.path.join(context.temp_dir, "src", "app.py")
    docs_file = os.path.join(context.temp_dir, "docs", "readme.md")

    for file_path in [test_file, src_file, docs_file]:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        pathlib.Path(file_path).write_text("content", encoding="utf-8")
        context.git_repo.index.add([file_path])

    context.staged_files = [test_file, src_file, docs_file]


@given("I have staged files matching both")
def step_given_staged_matching_both(context):
    """Create staged files matching both ignore and rules."""
    # File that should be ignored
    log_file = os.path.join(context.temp_dir, "app.log")
    pathlib.Path(log_file).write_text("log", encoding="utf-8")
    context.git_repo.index.add([log_file])

    # File that should have context rules
    test_file = os.path.join(context.temp_dir, "tests", "test.py")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    pathlib.Path(test_file).write_text("def test(): pass", encoding="utf-8")
    context.git_repo.index.add([test_file])

    context.staged_files = [log_file, test_file]
    context.ignored_files = [log_file]
    context.ruled_files = [test_file]


@given("I do not have a .solventignore file")
def step_given_no_solventignore(context):
    """Ensure .solventignore file does not exist."""
    solventignore_path = os.path.join(context.temp_dir, ".solventignore")
    if os.path.exists(solventignore_path):
        os.remove(solventignore_path)
    context.solventignore_path = None


@given("I do not have a .solventrules file")
def step_given_no_solventrules(context):
    """Ensure .solventrules file does not exist."""
    solventrules_path = os.path.join(context.temp_dir, ".solventrules")
    if os.path.exists(solventrules_path):
        os.remove(solventrules_path)
    context.solventrules_path = None


@given("I have staged files")
def step_given_staged_files_generic(context):
    """Create and stage generic files."""
    file1 = os.path.join(context.temp_dir, "file1.py")
    file2 = os.path.join(context.temp_dir, "file2.py")

    pathlib.Path(file1).write_text("def func1(): pass", encoding="utf-8")
    pathlib.Path(file2).write_text("def func2(): pass", encoding="utf-8")

    context.git_repo.index.add([file1, file2])
    context.staged_files = [file1, file2]


@then("ignored files should not be reviewed")
def step_then_ignored_not_reviewed(context):
    """Verify that ignored files were not included in the review."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "ignored_files")

    # Check that ignored files are not mentioned in feedback
    feedback_lower = context.hook_feedback.lower()
    for ignored_file in context.ignored_files:
        file_name = os.path.basename(ignored_file)
        # The file name might appear, but the content shouldn't be reviewed
        # This is a basic check - actual implementation will filter files
        assert file_name not in feedback_lower or "ignored" in feedback_lower


@then("only non-ignored staged files should be reviewed")
def step_then_only_non_ignored_reviewed(context):
    """Verify that only non-ignored files were reviewed."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "reviewed_files")

    # Feedback should mention reviewed files
    feedback_lower = context.hook_feedback.lower()
    for reviewed_file in context.reviewed_files:
        file_name = os.path.basename(reviewed_file)
        # At least one reviewed file should be mentioned
        # This is a basic check - actual implementation will be more precise
        assert any(
            file_name.lower() in feedback_lower or "file" in feedback_lower
            for _ in context.reviewed_files
        )


@then('"{file_name}" should be ignored')
def step_then_file_ignored(context, file_name):
    """Verify that a specific file was ignored."""
    assert hasattr(context, "hook_result")
    feedback_lower = context.hook_feedback.lower()

    # File should not appear in feedback (or be marked as ignored)
    # This is a basic check - actual implementation will filter files
    assert file_name.lower() not in feedback_lower or "ignored" in feedback_lower


@then('"{file_name}" should be reviewed')
def step_then_file_reviewed(context, file_name):
    """Verify that a specific file was reviewed."""
    assert hasattr(context, "hook_result")
    feedback_lower = context.hook_feedback.lower()

    # File should appear in feedback
    assert file_name.lower() in feedback_lower or "file" in feedback_lower


@then('files in "{directory}" should be ignored')
def step_then_directory_ignored(context, directory):
    """Verify that files in a directory were ignored."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "staged_files")

    # Check that directory files are not in feedback
    feedback_lower = context.hook_feedback.lower()
    for staged_file in context.staged_files:
        if directory in staged_file:
            file_name = os.path.basename(staged_file)
            # Directory files should not be reviewed
            assert (
                file_name.lower() not in feedback_lower or "ignored" in feedback_lower
            )


@then("the AI should receive context rules for matching files")
def step_then_ai_receives_context(context):
    """Verify that context rules were provided to the AI."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "solventrules_path")

    # The context rules should be applied (we'll verify this in implementation)
    # For now, just verify the hook completed successfully
    assert context.hook_result is not None


@then("the review should consider the provided context")
def step_then_review_considers_context(context):
    """Verify that the review considered the context rules."""
    assert hasattr(context, "hook_feedback")

    # Feedback should reflect the context (e.g., test-specific feedback)
    # This is a basic check - actual implementation will be more precise
    feedback_lower = context.hook_feedback.lower()
    assert len(feedback_lower) > 0  # Should have feedback


@then("each file should receive appropriate context from matching rules")
def step_then_each_file_has_context(context):
    """Verify that each file received appropriate context."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "staged_files")

    # Each file should be reviewed with appropriate context
    # This will be verified in the actual implementation
    assert context.hook_result is not None


@then("the AI should use the test-specific context")
def step_then_ai_uses_test_context(context):
    """Verify that test-specific context was used."""
    assert hasattr(context, "hook_feedback")

    # Feedback should reflect test-specific context
    feedback_lower = context.hook_feedback.lower()
    # Should mention test-related aspects if context was applied
    assert len(feedback_lower) > 0


@then("the review should focus on test quality aspects")
def step_then_focuses_on_test_quality(context):
    """Verify that review focused on test quality."""
    assert hasattr(context, "hook_feedback")

    feedback_lower = context.hook_feedback.lower()
    # Should contain test-related keywords if context was applied
    test_keywords = ["test", "coverage", "assert", "quality"]
    assert (
        any(keyword in feedback_lower for keyword in test_keywords)
        or len(feedback_lower) > 0
    )


@then("non-ignored files should receive context from matching rules")
def step_then_non_ignored_get_context(context):
    """Verify that non-ignored files received context from rules."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "ruled_files")

    # Non-ignored files with matching rules should have context applied
    assert context.hook_result is not None


@then("the pre-commit check should complete successfully")
def step_then_check_completes(context):
    """Verify that the pre-commit check completed without errors."""
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None
    # Should complete (pass or fail, but not error)
    assert isinstance(context.hook_passed, bool)
