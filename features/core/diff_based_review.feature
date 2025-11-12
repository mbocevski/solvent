Feature: Diff-Based Review
  As a developer
  I want the AI to review only the changes I made
  So that it can focus on what changed and be more efficient

  Background:
    Given I have a git repository

  Scenario: Review shows diff for modified files
    Given I have a file in the repository with content
      """
      def old_function():
          return "old"
      """
    And I have modified that file with new content
    And I have staged the modified file
    When I run the pre-commit hook
    Then the AI should receive the diff showing what changed
    And the AI should receive the original file for context
    And the pre-commit check should complete successfully

  Scenario: Review shows full content for new files
    Given I have staged a new file that doesn't exist in the repository
    When I run the pre-commit hook
    Then the AI should receive the full file content
    And the AI should not receive a diff
    And the pre-commit check should complete successfully

  Scenario: Review handles deleted files
    Given I have a file in the repository
    And I have staged the deletion of that file
    When I run the pre-commit hook
    Then the AI should receive information about the deletion
    And the pre-commit check should complete successfully

  Scenario: Review handles multiple files with mixed changes
    Given I have a modified file staged
    And I have a new file staged
    When I run the pre-commit hook
    Then the AI should receive appropriate information for each file type
    And the pre-commit check should complete successfully

