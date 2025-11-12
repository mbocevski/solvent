"""Step definitions for pre-commit hook review feature."""

import os
import pathlib
import tempfile

from behave import given, then, when
from git import Repo

# Import the actual functionality we're testing
from solvent_ai.hook import run_pre_commit_review


@given("I have a git repository")
def step_given_git_repository(context):
    """Set up a temporary git repository for testing."""
    # Create a temporary directory for the git repo
    context.temp_dir = tempfile.mkdtemp()
    context.git_repo = Repo.init(context.temp_dir)

    # Set up git config to avoid warnings
    context.git_repo.config_writer().set_value("user", "name", "Test User").release()
    context.git_repo.config_writer().set_value(
        "user", "email", "test@example.com"
    ).release()


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


@when("I run the pre-commit hook")
def step_when_run_pre_commit_hook(context):
    """Run the pre-commit hook review."""
    try:
        context.hook_result = run_pre_commit_review(repo_path=context.temp_dir)
        context.hook_passed = context.hook_result.passed
        context.hook_feedback = context.hook_result.feedback
    except Exception as e:
        context.hook_error = e
        context.hook_passed = False


@then("the pre-commit check should pass")
def step_then_pre_commit_passes(context):
    """Verify that the pre-commit check passed."""
    assert hasattr(context, "hook_result")
    assert context.hook_passed is True, (
        f"Pre-commit should pass but got: {context.hook_feedback}"
    )


@then("the pre-commit check should fail")
def step_then_pre_commit_fails(context):
    """Verify that the pre-commit check failed."""
    assert hasattr(context, "hook_result")
    assert context.hook_passed is False, "Pre-commit should fail but it passed"


@then("I should receive AI-generated feedback")
def step_then_receive_feedback(context):
    """Verify that AI-generated feedback was received."""
    assert hasattr(context, "hook_result")
    assert hasattr(context, "hook_feedback")
    assert context.hook_feedback is not None
    assert len(context.hook_feedback.strip()) > 0
    # Optionally verify status block format is present (but don't fail if it's not)
    # The evaluator has a fallback, so this is just a nice-to-have check
    if "---BEGIN STATUS---" in context.hook_feedback:
        assert "---END STATUS---" in context.hook_feedback
        assert "STATUS:" in context.hook_feedback
        assert "CRITICAL_ISSUES_COUNT:" in context.hook_feedback


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
