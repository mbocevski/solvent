"""Step definitions for max_tokens configuration feature."""

import os

from behave import given, then

from solvent_ai.ai.anthropic import AnthropicClient
from solvent_ai.ai.factory import create_ai_client
from solvent_ai.ai.gemini import GeminiClient
from solvent_ai.ai.openai import OpenAIClient


@given('the environment variable "{env_var}" is set to "{value}"')
def step_given_env_var_set(context, env_var, value):
    """Set an environment variable to a specific value."""
    os.environ[env_var] = value
    # Store in context for cleanup if needed
    if not hasattr(context, "env_vars"):
        context.env_vars = {}
    context.env_vars[env_var] = value


@given('the environment variable "{env_var}" is not set')
def step_given_env_var_not_set(context, env_var):
    """Remove an environment variable if it exists."""
    if env_var in os.environ:
        del os.environ[env_var]
    # Track for cleanup
    if not hasattr(context, "env_vars_to_remove"):
        context.env_vars_to_remove = []
    if env_var not in context.env_vars_to_remove:
        context.env_vars_to_remove.append(env_var)


@then("the Gemini client should be initialized with max_output_tokens set to {value}")
def step_then_gemini_max_tokens(context, value):
    """Verify Gemini client was initialized with correct max_output_tokens."""

    # Create client and check the attribute
    client = create_ai_client()
    assert isinstance(client, GeminiClient), (
        f"Expected GeminiClient, got {type(client)}"
    )

    expected_value = None if value == "None" else int(value)
    assert client.max_output_tokens == expected_value, (
        f"Expected max_output_tokens={expected_value}, got {client.max_output_tokens}"
    )


@then("the OpenAI client should be initialized with max_tokens set to {value}")
def step_then_openai_max_tokens(context, value):
    """Verify OpenAI client was initialized with correct max_tokens."""

    # Create client and check the attribute
    client = create_ai_client()
    assert isinstance(client, OpenAIClient), (
        f"Expected OpenAIClient, got {type(client)}"
    )

    expected_value = None if value == "None" else int(value)
    assert client.max_tokens == expected_value, (
        f"Expected max_tokens={expected_value}, got {client.max_tokens}"
    )


@then("the Anthropic client should be initialized with max_tokens set to {value}")
def step_then_anthropic_max_tokens(context, value):
    """Verify Anthropic client was initialized with correct max_tokens."""

    # Create client and check the attribute
    client = create_ai_client()
    assert isinstance(client, AnthropicClient), (
        f"Expected AnthropicClient, got {type(client)}"
    )

    expected_value = int(value)
    assert client.max_tokens == expected_value, (
        f"Expected max_tokens={expected_value}, got {client.max_tokens}"
    )
