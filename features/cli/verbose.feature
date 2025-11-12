Feature: Verbose Flag
  As a developer
  I want to enable verbose logging via command-line flag
  So that I can quickly see debug output without changing environment variables

  Background:
    Given I have a git repository

  Scenario: --verbose flag increases log verbosity
    Given I have staged files with good code
    When I run the pre-commit hook with --verbose
    Then the pre-commit check should complete successfully
    And verbose logging should be enabled

