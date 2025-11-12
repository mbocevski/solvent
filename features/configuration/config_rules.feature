Feature: Configuration Rules and Ignores
  As a developer
  I want to configure ignore patterns and review context rules for Solvent
  So that the AI can provide better reviews with project-specific context

  Background:
    Given I have a git repository

  Scenario: Files matching .solventignore patterns are excluded from review
    Given I have a .solventignore file with patterns
    And I have staged files including ignored files
    When I run the pre-commit hook
    Then ignored files should not be reviewed
    And only non-ignored staged files should be reviewed

  Scenario: .solventignore supports gitignore-style patterns
    Given I have a .solventignore file with pattern "*.log"
    And I have staged files including "app.log" and "code.py"
    When I run the pre-commit hook
    Then "app.log" should be ignored
    And "code.py" should be reviewed

  Scenario: Directory patterns in .solventignore work correctly
    Given I have a .solventignore file with pattern "vendor/"
    And I have staged files in "vendor/" directory
    When I run the pre-commit hook
    Then files in "vendor/" should be ignored

  Scenario: Context rules from .solventrules are applied to matching files
    Given I have a .solventrules file with context rules
    And I have staged files matching the rule patterns
    When I run the pre-commit hook
    Then the AI should receive context rules for matching files
    And the review should consider the provided context

  Scenario: Multiple context rules can be defined
    Given I have a .solventrules file with multiple rules
    And I have staged files matching different rule patterns
    When I run the pre-commit hook
    Then each file should receive appropriate context from matching rules

  Scenario: Context rules override default behavior for specific patterns
    Given I have a .solventrules file with a rule for "tests/**"
    And the rule specifies "This is test code, focus on test quality"
    And I have staged files in "tests/" directory
    When I run the pre-commit hook
    Then the AI should use the test-specific context
    And the review should focus on test quality aspects

  Scenario: Files matching both ignore and rules are handled correctly
    Given I have a .solventignore file
    And I have a .solventrules file
    And I have staged files matching both
    When I run the pre-commit hook
    Then ignored files should not be reviewed
    And non-ignored files should receive context from matching rules

  Scenario: Missing .solventignore and .solventrules files are handled gracefully
    Given I do not have a .solventignore file
    And I do not have a .solventrules file
    And I have staged files
    When I run the pre-commit hook
    Then all staged files should be reviewed
    And the pre-commit check should complete successfully

