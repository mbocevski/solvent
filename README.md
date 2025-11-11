# Solvent

AI-powered pre-commit hook for automated code review using Google Gemini.
Solvent automatically reviews your staged files before committing, blocking
commits with critical issues while providing actionable suggestions for
improvement.

## Features

- **Automated Pre-commit Reviews**: Seamlessly integrates with git pre-commit
  hooks
- **AI-Powered Analysis**: Uses Google Gemini for intelligent code review
- **Smart Blocking**: Blocks commits with critical issues (security
  vulnerabilities, dangerous operations, critical bugs)
- **Actionable Feedback**: Provides suggestions for non-critical improvements
  without blocking commits
- **Multi-file Support**: Handles multiple staged files in a single review
- **Configurable Ignore Patterns**: Exclude files from review using
  `.solventignore` (gitignore-style patterns)
- **File-Specific Context**: Provide custom AI context per file/directory using
  `.solventrules`
- **BDD Testing**: Comprehensive test coverage using behave

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast and reliable
dependency management.

```bash
# Install dependencies
uv sync

# Install with dev dependencies (for development)
uv sync --group dev
```

## Configuration

### Environment Variables

Solvent uses environment variables for configuration. All settings use the
`SOLVENT_` prefix and are case-insensitive.

**Required:**

```bash
export SOLVENT_GEMINI_API_KEY="your-api-key-here"
```

**Optional:**

```bash
export SOLVENT_GEMINI_MODEL="gemini-2.5-flash"  # Default: gemini-2.5-flash
export SOLVENT_GEMINI_TEMPERATURE="0.7"         # Default: 0.7 (range: 0.0-2.0)
export SOLVENT_LOG_LEVEL="INFO"                 # Default: INFO
```

> **Note**: Get your Gemini API key from
> [Google AI Studio](https://makersuite.google.com/app/apikey).

### Ignore Patterns (`.solventignore`)

Create a `.solventignore` file in your repository root to exclude files from AI
review. Uses gitignore-style pattern matching, powered by the `pathspec`
library.

**Example `.solventignore`:**

```gitignore
# Ignore log files
*.log
*.tmp

# Ignore build artifacts
build/
dist/
*.egg-info/

# Ignore vendor and dependency directories
vendor/
node_modules/
.venv/

# Ignore specific paths
/temp_dir/
**/cache/
```

**Behavior:**

- Files matching these patterns are excluded from review
- The pre-commit hook passes automatically if all staged files are ignored
- Patterns support all gitignore-style syntax (wildcards, negation, etc.)
- Patterns are evaluated relative to the repository root

### Context Rules (`.solventrules`)

Create a `.solventrules` file in your repository root to provide custom context
to the AI for specific files or directories. This helps the AI understand your
project structure and provide more relevant, context-aware reviews.

**File Format:**

The `.solventrules` file uses an INI-style format:

```ini
[pattern]
context = Context description for matching files

[another/pattern/**]
context = Different context for other files
```

**Example `.solventrules`:**

```ini
# Test files - focus on test quality and coverage
[tests/**]
context = This is test code. Focus on test quality, coverage, edge cases, and correctness.

# Documentation - focus on clarity and completeness
[docs/**]
context = This is documentation. Focus on clarity, grammar, completeness, and accuracy.

# Production code - be strict about security and performance
[src/**]
context = This is production code. Be strict about security, performance, and best practices.

# API endpoints - check for security vulnerabilities
[src/api/**]
context = This is API code. Check for security vulnerabilities, input validation, error handling, and authentication.

# Configuration files - check for secrets
[*.config]
[*.env]
context = This is a configuration file. Check for hardcoded secrets, credentials, and security issues.
```

**Pattern Matching:**

- Uses gitignore-style patterns (same syntax as `.solventignore`)
- Supports wildcards: `*.py`, `**/tests/`, `src/**`
- First matching rule wins (order matters - place more specific patterns first)
- Patterns are evaluated relative to the repository root

**Benefits:**

- **Test files**: Reviewed with test-specific criteria (coverage, edge cases)
- **Documentation**: Gets grammar and clarity checks
- **Production code**: Receives stricter security and performance reviews
- **Configuration files**: Gets secret and credential detection
- **Custom contexts**: Tailor reviews to your project's specific needs

## Usage

### Command Line

After setting your `SOLVENT_GEMINI_API_KEY` environment variable:

```bash
# Review staged files
uv run solvent

# Or if installed globally
solvent
```

The command will:

- Exit with code 0 if the review passes
- Exit with code 1 if critical issues are found
- Print detailed feedback to stdout

### Programmatic Usage

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

Solvent integrates seamlessly with the [pre-commit](https://pre-commit.com/)
framework. Choose one of the following options:

#### Option 1: Local Hook (Recommended for Development)

First, install Solvent in your project:

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

If using `uv` without installing globally:

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

#### Option 2: Repository Hook (When Published)

Once Solvent is published to a git repository, you can use it as a repository
hook:

```yaml
repos:
  - repo: https://github.com/yourusername/solvent
    rev: v0.1.0 # Use a specific version or tag
    hooks:
      - id: solvent
```

> **Important**: Make sure to set the `SOLVENT_GEMINI_API_KEY` environment
> variable before running pre-commit hooks. You can set it in your shell profile
> or use a tool like `direnv` for project-specific environment variables.

## How It Works

Solvent follows a streamlined workflow to review your code:

1. **Detects Staged Files**: Scans the git repository for all files staged for
   commit
2. **Applies Ignore Patterns**: Filters out files matching `.solventignore`
   patterns (if present)
3. **Loads Context Rules**: Loads file-specific context from `.solventrules` (if
   present)
4. **Reads File Contents**: Reads the contents of non-ignored staged files
   (skips binary files and files with encoding errors)
5. **AI Review**: Sends files to Google Gemini for review, including
   file-specific context where applicable
6. **Determines Pass/Fail**: Analyzes AI feedback for critical issues using:
   - Machine-readable status block (preferred)
   - Keyword-based fallback detection
7. **Returns Result**: Returns `HookResult` with pass/fail status and detailed
   feedback

### Critical Issues That Block Commits

The following issues will cause the pre-commit hook to fail:

- **Security Vulnerabilities**: SQL injection, XSS, code injection, remote code
  execution, etc.
- **Dangerous Operations**: Unintended file deletion, system command execution,
  unsafe file operations
- **Critical Bugs**: Issues that could cause data loss, system failures, or
  production outages
- **Unsafe Code Patterns**: Code that introduces significant risk or violates
  safety requirements
- **Hardcoded Secrets**: Credentials, API keys, or sensitive information in code

### Non-Critical Issues

The following issues will be reported but will **not** block the commit:

- Code style violations (formatting, naming conventions)
- Minor code quality improvements (refactoring opportunities)
- Performance optimizations that don't affect correctness
- Documentation improvements
- Best practice suggestions that don't introduce immediate risk

These suggestions are included in the feedback to help improve code quality over
time without blocking your workflow.

## Examples

### Example 1: Basic Usage

```bash
# Set your API key
export SOLVENT_GEMINI_API_KEY="your-api-key"

# Stage some files
git add src/app.py tests/test_app.py

# Run review
uv run solvent

# Output will show:
# - Status (PASS/FAIL)
# - Critical issues (if any)
# - Suggestions for improvement
```

### Example 2: Using `.solventignore`

Create `.solventignore` in your repository root:

```gitignore
# Ignore build artifacts
*.log
*.tmp
build/
dist/
.venv/

# Ignore vendor dependencies
vendor/
node_modules/
```

Now when you commit, these files are automatically excluded from review. If all
staged files match ignore patterns, the hook passes immediately without calling
the AI.

### Example 3: Using `.solventrules`

Create `.solventrules` in your repository root:

```ini
[tests/**]
context = This is test code. Focus on test quality, coverage, and edge cases.

[src/api/**]
context = This is API code. Check for security vulnerabilities, input validation, and error handling.

[docs/**]
context = This is documentation. Focus on clarity, completeness, and accuracy.
```

The AI will now provide context-aware reviews:

- **Test files**: Reviewed for test quality, coverage, and correctness
- **API files**: Security-focused reviews with emphasis on vulnerabilities
- **Documentation**: Grammar and clarity checks

### Example 4: Combined Usage

Use both `.solventignore` and `.solventrules` together for maximum control:

**`.solventignore`:**

```gitignore
*.log
build/
dist/
```

**`.solventrules`:**

```ini
[src/**]
context = Production code - be strict about security and performance

[tests/**]
context = Test code - focus on quality and coverage
```

**Result:**

- Log files and build artifacts are ignored (not reviewed)
- Source files get strict security and performance reviews
- Test files get quality-focused reviews
- Other files get default reviews

## Project Structure

```
solvent/
├── src/solvent/
│   ├── __init__.py              # Main package exports
│   ├── main.py                  # CLI entry point
│   ├── hook/
│   │   ├── __init__.py          # Hook module exports
│   │   ├── orchestrator.py      # Pre-commit hook orchestration
│   │   └── evaluator.py         # Pass/fail evaluation logic
│   ├── ai/
│   │   ├── __init__.py          # AI module exports
│   │   ├── gemini_client.py     # Google Gemini API integration
│   │   └── context.py           # AI prompt context and templates
│   ├── config/
│   │   ├── __init__.py          # Config module exports
│   │   ├── logging_config.py    # Logging setup and configuration
│   │   └── settings.py          # Application settings (pydantic)
│   ├── git/
│   │   ├── __init__.py          # Git module exports
│   │   └── repository.py        # Git operations (staged files, etc.)
│   ├── rules/
│   │   ├── __init__.py          # Rules module exports
│   │   ├── ignore.py            # .solventignore pattern handling
│   │   └── context.py           # .solventrules context rule handling
│   └── models/
│       ├── __init__.py          # Models module exports
│       └── hook.py              # HookResult data model
├── features/                    # BDD feature files (behave)
│   ├── environment.py           # Behave environment setup/teardown
│   ├── git_commit_review.feature
│   ├── config_rules.feature
│   └── steps/
│       ├── git_commit_review_steps.py
│       └── config_rules_steps.py
└── pyproject.toml               # Project configuration and dependencies
```

## Development

### Prerequisites

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) for dependency management
- Google Gemini API key (for running tests)

### Running Tests

This project uses [behave](https://behave.readthedocs.io/) for Behavior-Driven
Development (BDD) testing.

```bash
# Run all tests
uv run behave

# Dry run (see what would be executed without running)
uv run behave --dry-run

# Run with specific output format
uv run behave --format json
uv run behave --format json.pretty

# Run specific feature
uv run behave features/config_rules.feature
```

### Code Quality

We use `ruff` for linting and formatting, and `pyright` for type checking:

```bash
# Run linter
uv run ruff check src/solvent

# Auto-fix linting issues
uv run ruff check --fix src/solvent

# Format code
uv run ruff format

# Type checking
uv run pyright src/solvent

# Run all quality checks
uv run ruff check src/solvent && uv run ruff format && uv run pyright src/solvent
```

### Development Workflow

1. Create a feature branch
2. Make your changes
3. Write or update tests
4. Run tests: `uv run behave`
5. Check code quality: `uv run ruff check --fix && uv run pyright`
6. Format code: `uv run ruff format`
7. Commit your changes

## Requirements

- **Python**: >= 3.10
- **Google Gemini API Key**: Required for AI reviews
  ([Get one here](https://makersuite.google.com/app/apikey))
- **Git Repository**: Solvent operates on git repositories
- **Dependencies**: Automatically installed via `uv sync`:
  - `google-genai`: Google Gemini API client
  - `GitPython`: Git repository operations
  - `pydantic` / `pydantic-settings`: Configuration management
  - `pathspec`: Pattern matching for ignore/rules files

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
