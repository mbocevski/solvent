"""Behave environment configuration for setup and teardown hooks."""

import contextlib
import os
import shutil
from unittest.mock import MagicMock, patch

from features.mocks import get_mock_response_for_scenario
from solvent_ai.config import reset_settings


def before_all(context):
    """Run before all features."""
    # Initialize any global test data or configuration
    # Don't mock for integration/e2e tests - they should use real API
    context.ai_client_patcher = None
    context.mock_ai_client = None


def before_feature(context, feature):
    """Run before each feature."""
    # Check if this is an integration/e2e test - if so, don't mock
    is_integration = any(
        tag in {"integration", "e2e"}
        for tag in feature.tags
        if hasattr(feature, "tags")
    )

    if not is_integration:
        # Patch create_ai_client to use mocks instead of real API calls
        # Patch where it's imported in orchestrator
        context.ai_client_patcher = patch(
            "solvent_ai.hook.orchestrator.create_ai_client"
        )
        context.mock_ai_client = context.ai_client_patcher.start()

        def mock_review_staged_files(file_info_dict, context_rules=None):
            """Mock implementation of review_staged_files."""
            # Use file info to determine appropriate mock response
            # We don't need scenario name since file info is sufficient
            return get_mock_response_for_scenario("", file_info_dict)

        # Create a mock instance
        mock_instance = MagicMock()
        mock_instance.review_staged_files = MagicMock(
            side_effect=mock_review_staged_files
        )
        context.mock_ai_client.return_value = mock_instance


def after_all(context):
    """Run after all features."""
    # Cleanup any global resources
    # Stop the patcher if it was created
    if hasattr(context, "ai_client_patcher") and context.ai_client_patcher is not None:
        context.ai_client_patcher.stop()


def after_feature(context, feature):
    """Run after each feature."""
    # Stop the patcher after each feature if it was created
    if hasattr(context, "ai_client_patcher") and context.ai_client_patcher is not None:
        context.ai_client_patcher.stop()
        context.ai_client_patcher = None
        context.mock_ai_client = None


def before_scenario(context, scenario):
    """Run before each scenario."""
    # Reset settings singleton to pick up new environment variables
    reset_settings()

    # Set required environment variables for tests
    # Only set dummy API keys if they're not already set
    # (for integration/e2e tests that need real keys from environment)
    # Set default provider to gemini for mocked tests
    if "SOLVENT_AI_PROVIDER" not in os.environ:
        os.environ["SOLVENT_AI_PROVIDER"] = "gemini"
    if "SOLVENT_GEMINI_API_KEY" not in os.environ:
        # Use a dummy API key since we're mocking the API calls
        os.environ["SOLVENT_GEMINI_API_KEY"] = "test-gemini-key-for-mocked-tests"
    if "SOLVENT_OPENAI_API_KEY" not in os.environ:
        # Use a dummy API key since we're mocking the API calls
        os.environ["SOLVENT_OPENAI_API_KEY"] = "test-openai-key-for-mocked-tests"
    if "SOLVENT_ANTHROPIC_API_KEY" not in os.environ:
        # Use a dummy API key since we're mocking the API calls
        os.environ["SOLVENT_ANTHROPIC_API_KEY"] = "test-anthropic-key-for-mocked-tests"

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
