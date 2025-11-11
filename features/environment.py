"""Behave environment configuration for setup and teardown hooks."""

import contextlib
import shutil
from unittest.mock import MagicMock, patch

from features.mocks import get_mock_response_for_scenario


def before_all(context):
    """Run before all features."""
    # Initialize any global test data or configuration
    # Don't mock for integration/e2e tests - they should use real API
    context.gemini_patcher = None
    context.mock_gemini_client_class = None


def before_feature(context, feature):
    """Run before each feature."""
    # Check if this is an integration/e2e test - if so, don't mock
    is_integration = any(
        tag in {"integration", "e2e"}
        for tag in feature.tags
        if hasattr(feature, "tags")
    )

    if not is_integration:
        # Patch GeminiClient to use mocks instead of real API calls
        # Patch where it's imported in orchestrator
        context.gemini_patcher = patch("solvent.hook.orchestrator.GeminiClient")
        context.mock_gemini_client_class = context.gemini_patcher.start()

        def mock_review_staged_files(file_contents, context_rules=None):
            """Mock implementation of review_staged_files."""
            # Use file contents to determine appropriate mock response
            # We don't need scenario name since file contents are sufficient
            return get_mock_response_for_scenario("", file_contents)

        # Create a mock instance
        mock_instance = MagicMock()
        mock_instance.review_staged_files = MagicMock(
            side_effect=mock_review_staged_files
        )
        context.mock_gemini_client_class.return_value = mock_instance


def after_all(context):
    """Run after all features."""
    # Cleanup any global resources
    # Stop the patcher if it was created
    if hasattr(context, "gemini_patcher") and context.gemini_patcher is not None:
        context.gemini_patcher.stop()


def after_feature(context, feature):
    """Run after each feature."""
    # Stop the patcher after each feature if it was created
    if hasattr(context, "gemini_patcher") and context.gemini_patcher is not None:
        context.gemini_patcher.stop()
        context.gemini_patcher = None
        context.mock_gemini_client_class = None


def before_scenario(context, scenario):
    """Run before each scenario."""
    # Initialize scenario-specific context
    context.git_repo = None
    context.commits = []
    context.review_results = []
    context.scenario_name = scenario.name if hasattr(scenario, "name") else ""


def after_scenario(context, scenario):
    """Run after each scenario."""
    # Cleanup scenario-specific resources
    if hasattr(context, "temp_dir") and context.temp_dir:
        # Cleanup temporary directory
        with contextlib.suppress(Exception):
            shutil.rmtree(context.temp_dir)
