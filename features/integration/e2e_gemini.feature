@integration @e2e @gemini
Feature: End-to-End Integration Test with Gemini
  As a developer
  I want to verify that Solvent works correctly with the real Gemini API
  So that I can be confident the Gemini integration is working properly

  Background:
    Given I have a git repository
    And the AI provider is set to "gemini"

  Scenario: E2E test passes with good code
    Given I have staged files with good code for e2e
    When I run the pre-commit hook
    Then the pre-commit check should pass
    And I should receive AI-generated feedback

  Scenario: E2E test fails with problematic code
    Given I have staged files with problematic code for e2e
    When I run the pre-commit hook
    Then the pre-commit check should fail
    And I should receive feedback explaining why it failed

