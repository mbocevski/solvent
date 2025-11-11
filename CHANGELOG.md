# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-11

Initial release of Solvent.

### Added

- **Pre-commit Hook**: AI-powered pre-commit hook that reviews staged files
  using Google Gemini before commits
- **Google Gemini Integration**: Seamless integration with Google Gemini API for
  intelligent code review
- **Diff-Based Review**: Efficient review system that sends git diffs and
  original file content to the AI, focusing on what changed rather than entire
  files. This significantly reduces API token usage and provides better context
  for code reviews:
  - Modified files: Shows diff of changes + original file for context
  - New files: Shows full file content
  - Deleted files: Shows diff of what was removed + original file
- **Configurable Ignore Patterns**: Support for `.solventignore` file with
  gitignore-style patterns to exclude files from review
- **File-Specific Context Rules**: Support for `.solventrules` file to provide
  custom AI context per file or directory pattern
- **File Size Limits**: Automatic skipping of files larger than configured limit
  (default: 1MB) to prevent API token limits and timeouts
- **Retry Logic**: Automatic retry with exponential backoff for transient API
  errors (503, 429, 502, 504, network errors)
- **Machine-Readable Status**: Status block in AI responses for reliable
  pass/fail detection
- **CLI Interface**: Command-line interface with `--help`, `--version`, and
  `--verbose` flags
- **Comprehensive Testing**: Full BDD test suite using behave with mocked tests
  and end-to-end integration tests
- **Error Handling**: User-friendly error messages for different API error types
  (503, 429, 401, 403)
- **Logging Configuration**: Configurable logging levels with suppression of
  verbose external library logs
- **MIT License**: Open-source license for the project

### Changed

- Enhanced AI prompt with detailed pre-commit context and instructions for
  better review quality
- Improved error messages for better user experience

### Fixed

- Reliable detection of staged files in new Git repositories (before first
  commit)
- Proper handling of binary files and encoding errors
- Graceful handling when all files are ignored or too large
