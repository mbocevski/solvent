Feature: Pre-commit Hook Review
  As a developer
  I want to review staged files using AI before committing
  So that I can catch issues before they enter the repository

  Background:
    Given I have a git repository

  Scenario: Pre-commit hook passes with good code
    Given I have staged files with good code
    When I run the pre-commit hook
    Then the pre-commit check should pass
    And I should receive AI-generated feedback

  Scenario: Pre-commit hook fails with problematic code
    Given I have staged files with problematic code
    When I run the pre-commit hook
    Then the pre-commit check should fail
    And I should receive feedback explaining why it failed

  Scenario: Pre-commit hook reviews multiple staged files
    Given I have 3 staged files
    When I run the pre-commit hook
    Then all staged files should be reviewed
    And the pre-commit check result should be based on all files

  Scenario: Pre-commit hook passes with minor suggestions
    Given I have staged files with minor issues
    When I run the pre-commit hook
    Then the pre-commit check should pass
    And I should receive suggestions for improvement
