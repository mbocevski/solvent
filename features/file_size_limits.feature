Feature: File Size Limits
  As a developer
  I want large files to be automatically excluded from review
  So that I don't hit API token limits or timeouts with huge files

  Background:
    Given I have a git repository

  Scenario: Large files are automatically skipped
    Given I have staged a file larger than the size limit
    When I run the pre-commit hook
    Then the large file should be skipped from review
    And the pre-commit check should complete successfully
    And I should receive a message indicating the file was skipped

  Scenario: Files within size limit are reviewed normally
    Given I have staged a file smaller than the size limit
    When I run the pre-commit hook
    Then the file should be reviewed
    And the pre-commit check should complete successfully

  Scenario: Mixed large and small files are handled correctly
    Given I have staged both large and small files
    When I run the pre-commit hook
    Then large files should be skipped
    And small files should be reviewed
    And the pre-commit check should complete successfully

  Scenario: All files too large results in no review
    Given I have staged only files larger than the size limit
    When I run the pre-commit hook
    Then all files should be skipped
    And the pre-commit check should pass
    And I should receive a message indicating all files were skipped

