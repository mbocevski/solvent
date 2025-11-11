# Solvent

AI-powered pre-commit hook for code review using Google Gemini. Solvent reviews
your staged files before committing and blocks commits with critical issues
while providing suggestions for improvement.

## Features

- Pre-commit hook that reviews staged files
- AI-powered code review using Google Gemini
- Blocks commits with critical issues (security vulnerabilities, dangerous
  operations)
- Provides suggestions for non-critical improvements
- Handles multiple staged files
- BDD testing with behave

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency
management.

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --group dev
```

## Configuration

Solvent uses environment variables for configuration. Set the following:

```bash
export SOLVENT_GEMINI_API_KEY="your-api-key-here"
export SOLVENT_GEMINI_MODEL="gemini-2.5-flash"  # Optional, defaults to gemini-2.5-flash
export SOLVENT_GEMINI_TEMPERATURE="0.7"         # Optional, defaults to 0.7
export SOLVENT_LOG_LEVEL="INFO"                 # Optional, defaults to INFO
```

All configuration uses the `SOLVENT_` prefix and is case-insensitive.

## Usage

### As a Pre-commit Hook

```python
from solvent import run_pre_commit_review

# Run the pre-commit review
result = run_pre_commit_review()

if not result.passed:
    print("Pre-commit check failed!")
    print(result.feedback)
    exit(1)
else:
    print("Pre-commit check passed!")
    if result.feedback:
        print(result.feedback)  # Suggestions for improvement
```

### Integration with pre-commit Framework

Solvent can be used as a pre-commit hook in two ways:

#### Option 1: Local Hook (Recommended for development)

First, install solvent in your project:

```bash
# Using pip
pip install solvent

# Or using uv
uv add solvent
```

Then add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: solvent
        name: Solvent AI Code Review
        entry: solvent
        language: system
        pass_filenames: false
        require_serial: true
```

Or if using `uv` without installing globally:

```yaml
repos:
  - repo: local
    hooks:
      - id: solvent
        name: Solvent AI Code Review
        entry: uv run solvent
        language: system
        pass_filenames: false
        require_serial: true
```

#### Option 2: Repository Hook (When published)

Once solvent is published to a git repository, you can use it as a repository
hook:

```yaml
repos:
  - repo: https://github.com/yourusername/solvent
    rev: v0.1.0 # Use a specific version or tag
    hooks:
      - id: solvent
```

**Note**: Make sure to set the `SOLVENT_GEMINI_API_KEY` environment variable
before running pre-commit hooks.

## Project Structure

```
solvent/
├── src/solvent/
│   ├── __init__.py          # Main exports
│   ├── main.py              # CLI entry point
│   ├── hook/
│   │   ├── __init__.py      # Hook module exports
│   │   ├── orchestrator.py  # Pre-commit hook orchestration
│   │   └── evaluator.py     # Pass/fail evaluation logic
│   ├── ai/
│   │   ├── __init__.py
│   │   └── gemini_client.py # Gemini API integration
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logging_config.py # Logging setup
│   │   └── settings.py       # Configuration management
│   ├── git/
│   │   ├── __init__.py
│   │   └── repository.py    # Git operations (staged files, etc.)
│   └── models/
│       ├── __init__.py
│       └── hook.py           # HookResult data model
├── features/                # BDD feature files
│   ├── environment.py
│   ├── git_commit_review.feature
│   └── steps/
│       └── git_commit_review_steps.py
└── pyproject.toml
```

## Development

### Running Tests

This project uses [behave](https://behave.readthedocs.io/) for BDD testing.

```bash
# Run all tests
uv run behave

# Dry run (see what would be executed)
uv run behave --dry-run

# Run with specific format
uv run behave --format json
```

### Code Quality

```bash
# Run linter
uv run ruff check src/solvent

# Auto-fix linting issues
uv run ruff check --fix src/solvent

# Format code
uv run ruff format

# Type checking
uv run pyright src/solvent
```

## How It Works

1. **Detects Staged Files**: Finds all files staged for commit
2. **Reads File Contents**: Reads the contents of staged files
3. **AI Review**: Sends files to Google Gemini for review
4. **Determines Pass/Fail**: Analyzes feedback for critical issues
5. **Returns Result**: Returns `HookResult` with pass/fail status and feedback

### Critical Issues That Block Commits

- Security vulnerabilities (SQL injection, XSS, code injection, etc.)
- Dangerous operations (file deletion, system commands, etc.)
- Critical bugs that could cause data loss or system failures
- Unsafe code patterns

### Non-Critical Issues

- Code style suggestions
- Minor improvements
- Best practice recommendations

These will not block the commit but will be included in the feedback.

## Requirements

- Python >= 3.10
- Google Gemini API key
- Git repository

## License

(Add your license here)
