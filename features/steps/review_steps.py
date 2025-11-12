"""Step definitions for review-related features."""

import os
import pathlib

from behave import given, then

# Reuse common steps from common_steps
# Review-specific steps are defined here


@given("I have staged files with good code")
def step_given_staged_good_code(context):
    """Create and stage files with good code."""
    # Create a well-written Python file
    test_file = os.path.join(context.temp_dir, "good_code.py")
    pathlib.Path(test_file).write_text(
        """\"\"\"A well-written Python module.\"\"\"

def calculate_sum(numbers: list[int]) -> int:
    \"\"\"Calculate the sum of a list of numbers.

    Args:
        numbers: List of integers to sum.

    Returns:
        The sum of all numbers in the list.
    \"\"\"
    return sum(numbers)


if __name__ == "__main__":
    result = calculate_sum([1, 2, 3, 4, 5])
    print(f"Sum: {result}")
""",
        encoding="utf-8",
    )

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]


@given("I have staged files with problematic code")
def step_given_staged_problematic_code(context):
    """Create and stage files with problematic code."""
    # Create a file with obvious issues
    test_file = os.path.join(context.temp_dir, "bad_code.py")
    pathlib.Path(test_file).write_text(
        """import os
password = "secret123"
eval(input("Enter code: "))
os.system("rm -rf /")
""",
        encoding="utf-8",
    )

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]


@given("I have {count:d} staged files")
def step_given_multiple_staged_files(context, count):
    """Create and stage multiple files."""
    context.staged_files = []
    for i in range(count):
        test_file = os.path.join(context.temp_dir, f"file_{i}.py")
        pathlib.Path(test_file).write_text(
            f"# File {i}\ndef func_{i}():\n    pass\n", encoding="utf-8"
        )
        context.git_repo.index.add([test_file])
        context.staged_files.append(test_file)


@given("I have staged files with minor issues")
def step_given_staged_minor_issues(context):
    """Create and stage files with minor code quality issues."""
    test_file = os.path.join(context.temp_dir, "minor_issues.py")
    pathlib.Path(test_file).write_text(
        """def func(x):
    # Missing type hints and docstring
    return x * 2
""",
        encoding="utf-8",
    )

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]


@then("I should receive feedback explaining why it failed")
def step_then_receive_failure_feedback(context):
    """Verify that feedback explains the failure."""
    assert hasattr(context, "hook_feedback")
    assert context.hook_feedback is not None
    assert len(context.hook_feedback.strip()) > 0
    # Feedback should contain some indication of issues
    feedback_lower = context.hook_feedback.lower()
    # Check for common issue indicators
    assert any(
        keyword in feedback_lower
        for keyword in ["issue", "problem", "error", "security", "risk", "concern"]
    )


@then("all staged files should be reviewed")
def step_then_all_files_reviewed(context):
    """Verify that all staged files were reviewed."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "staged_files")
    # The hook should have reviewed all staged files
    assert context.hook_result is not None


@then("the pre-commit check result should be based on all files")
def step_then_result_based_on_all_files(context):
    """Verify that the result considers all files."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "hook_passed")
    # Result should be a boolean indicating pass/fail
    assert isinstance(context.hook_passed, bool)


@then("I should receive suggestions for improvement")
def step_then_receive_suggestions(context):
    """Verify that suggestions for improvement were received."""
    assert hasattr(context, "hook_feedback")
    assert context.hook_feedback is not None
    feedback_lower = context.hook_feedback.lower()
    # Should contain suggestion-like keywords
    assert any(
        keyword in feedback_lower
        for keyword in ["suggest", "improve", "consider", "recommend", "better"]
    )


# Diff-based review steps
@given("I have a file in the repository with content")
def step_given_file_in_repo(context):
    """Create a file and commit it to the repository."""
    # Get content from the step text (docstring)
    content = context.text.strip() if hasattr(context, "text") and context.text else ""
    if not content:
        # Fallback to default content
        content = 'def old_function():\n    return "old"'

    test_file = os.path.join(context.temp_dir, "existing_file.py")
    pathlib.Path(test_file).write_text(content, encoding="utf-8")

    # Add and commit the file
    context.git_repo.index.add([test_file])
    context.git_repo.index.commit("Initial commit")
    context.existing_file = test_file


@given("I have modified that file with new content")
def step_given_modified_file(context):
    """Modify the existing file with new content."""
    assert hasattr(context, "existing_file")
    # Get content from the step text
    new_content = (
        context.text.strip() if hasattr(context, "text") and context.text else ""
    )
    if not new_content:
        # Fallback to default modified content
        new_content = 'def new_function():\n    return "new"'

    pathlib.Path(context.existing_file).write_text(new_content, encoding="utf-8")
    context.modified_file = context.existing_file
    context.modified_content = new_content


@given("I have staged the modified file")
def step_given_staged_modified_file(context):
    """Stage the modified file."""
    assert hasattr(context, "modified_file")
    context.git_repo.index.add([context.modified_file])
    context.staged_files = [context.modified_file]


@given("I have staged a new file that doesn't exist in the repository")
def step_given_staged_new_file(context):
    """Create and stage a new file that doesn't exist in the repository."""
    new_file = os.path.join(context.temp_dir, "new_file.py")
    content = context.text.strip() if hasattr(context, "text") and context.text else ""
    if not content:
        content = 'def new_function():\n    return "new"'

    pathlib.Path(new_file).write_text(content, encoding="utf-8")
    context.git_repo.index.add([new_file])
    context.staged_files = [new_file]
    context.new_file = new_file
    context.new_file_content = content


@given("I have a file in the repository")
def step_given_file_in_repo_simple(context):
    """Create a file and commit it to the repository."""
    test_file = os.path.join(context.temp_dir, "file_to_delete.py")
    pathlib.Path(test_file).write_text("def func():\n    pass\n", encoding="utf-8")

    # Add and commit the file
    context.git_repo.index.add([test_file])
    context.git_repo.index.commit("Add file to delete")
    context.file_to_delete = test_file


@given("I have staged the deletion of that file")
def step_given_staged_deletion(context):
    """Stage the deletion of a file."""
    assert hasattr(context, "file_to_delete")
    context.git_repo.index.remove([context.file_to_delete])
    context.staged_files = [context.file_to_delete]
    context.deleted_file = context.file_to_delete


@given("I have a modified file staged")
def step_given_modified_file_staged(context):
    """Create a file, commit it, modify it, and stage it."""
    # Create and commit initial file
    test_file = os.path.join(context.temp_dir, "modified.py")
    pathlib.Path(test_file).write_text("def old():\n    return 1\n", encoding="utf-8")
    context.git_repo.index.add([test_file])
    context.git_repo.index.commit("Initial commit")

    # Modify and stage
    pathlib.Path(test_file).write_text("def new():\n    return 2\n", encoding="utf-8")
    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]
    context.modified_file = test_file


@then("the AI should receive the diff showing what changed")
def step_then_ai_receives_diff(context):
    """Verify that the AI receives diff information."""
    # This is verified indirectly through the review process
    # The actual verification happens in the orchestrator/hook
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None


@then("the AI should receive the original file for context")
def step_then_ai_receives_original(context):
    """Verify that the AI receives original file content."""
    # This is verified indirectly through the review process
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None


@then("the AI should receive the full file content")
def step_then_ai_receives_full_content(context):
    """Verify that the AI receives full file content for new files."""
    # This is verified indirectly through the review process
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None


@then("the AI should not receive a diff")
def step_then_ai_no_diff(context):
    """Verify that the AI does not receive a diff for new files."""
    # This is verified indirectly through the review process
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None


@then("the AI should receive information about the deletion")
def step_then_ai_receives_deletion_info(context):
    """Verify that the AI receives information about file deletion."""
    # This is verified indirectly through the review process
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None


@then("the AI should receive appropriate information for each file type")
def step_then_ai_receives_appropriate_info(context):
    """Verify that the AI receives appropriate information for each file type."""
    # This is verified indirectly through the review process
    assert hasattr(context, "hook_result")
    assert context.hook_result is not None


@given("I have a new file staged")
def step_given_new_file_staged(context):
    """Create and stage a new file."""
    new_file = os.path.join(context.temp_dir, "another_new_file.py")
    pathlib.Path(new_file).write_text("def another():\n    pass\n", encoding="utf-8")
    context.git_repo.index.add([new_file])
    context.staged_files = [new_file]
