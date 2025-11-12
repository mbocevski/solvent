Feature: Maximum Output Tokens Configuration
  As a developer
  I want to configure the maximum output tokens for AI responses
  So that I can control response length and manage API costs

  Background:
    Given I have a git repository

  Scenario: Gemini client uses configured max_tokens
    Given the AI provider is set to "gemini"
    And the environment variable "SOLVENT_MAX_TOKENS" is set to "2048"
    And I have staged files with good code
    When I run the pre-commit hook
    Then the Gemini client should be initialized with max_output_tokens set to 2048
    And the pre-commit check should pass

  Scenario: OpenAI client uses configured max_tokens
    Given the AI provider is set to "openai"
    And the environment variable "SOLVENT_MAX_TOKENS" is set to "1024"
    And I have staged files with good code
    When I run the pre-commit hook
    Then the OpenAI client should be initialized with max_tokens set to 1024
    And the pre-commit check should pass

  Scenario: Anthropic client uses configured max_tokens
    Given the AI provider is set to "anthropic"
    And the environment variable "SOLVENT_MAX_TOKENS" is set to "8192"
    And I have staged files with good code
    When I run the pre-commit hook
    Then the Anthropic client should be initialized with max_tokens set to 8192
    And the pre-commit check should pass

  Scenario: Default max_tokens values are used when not configured
    Given the AI provider is set to "gemini"
    And the environment variable "SOLVENT_MAX_TOKENS" is not set
    And I have staged files with good code
    When I run the pre-commit hook
    Then the Gemini client should be initialized with max_output_tokens set to None
    And the pre-commit check should pass

  Scenario: Anthropic uses default 4096 when max_tokens is not set
    Given the AI provider is set to "anthropic"
    And the environment variable "SOLVENT_MAX_TOKENS" is not set
    And I have staged files with good code
    When I run the pre-commit hook
    Then the Anthropic client should be initialized with max_tokens set to 4096
    And the pre-commit check should pass

