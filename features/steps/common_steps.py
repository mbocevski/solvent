"""Common step definitions used across multiple features."""

import tempfile

from behave import given, then, when
from git import Repo

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
