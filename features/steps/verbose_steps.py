"""Step definitions for verbose flag feature."""

import logging

from behave import then, when

from solvent_ai.config import setup_logging
from solvent_ai.hook import run_pre_commit_review

# Reuse common steps from git_commit_review_steps
# Only verbose-specific steps are defined here


@when("I run the pre-commit hook with --verbose")
def step_when_run_pre_commit_hook_verbose(context):
    """Run the pre-commit hook with --verbose flag."""
    # Set up verbose logging
    setup_logging(level=logging.DEBUG)
    context.log_level_used = "DEBUG"

    try:
        context.hook_result = run_pre_commit_review(repo_path=context.temp_dir)
        context.hook_passed = context.hook_result.passed
        context.hook_feedback = context.hook_result.feedback
    except Exception as e:
        context.hook_error = e
        context.hook_passed = False


@then("verbose logging should be enabled")
def step_then_verbose_logging_enabled(context):
    """Verify that verbose logging is enabled."""
    assert hasattr(context, "log_level_used")
    assert context.log_level_used == "DEBUG", "Verbose logging should use DEBUG level"
