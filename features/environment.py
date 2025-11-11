"""Behave environment configuration for setup and teardown hooks."""

import contextlib
import shutil


def before_all(context):
    """Run before all features."""
    # Initialize any global test data or configuration


def after_all(context):
    """Run after all features."""
    # Cleanup any global resources


def before_feature(context, feature):
    """Run before each feature."""


def after_feature(context, feature):
    """Run after each feature."""


def before_scenario(context, scenario):
    """Run before each scenario."""
    # Initialize scenario-specific context
    context.git_repo = None
    context.commits = []
    context.review_results = []


def after_scenario(context, scenario):
    """Run after each scenario."""
    # Cleanup scenario-specific resources
    if hasattr(context, "temp_dir") and context.temp_dir:
        # Cleanup temporary directory
        with contextlib.suppress(Exception):
            shutil.rmtree(context.temp_dir)
