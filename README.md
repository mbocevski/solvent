# Solvent

AI-powered pre-commit hook for automated code review. Solvent automatically
reviews your staged files before committing, blocking commits with critical
issues while providing actionable suggestions for improvement. Supports multiple
AI providers - choose the one that works best for you.

## Features

- **Automated Pre-commit Reviews**: Seamlessly integrates with git pre-commit
  hooks
- **AI-Powered Analysis**: Supports multiple AI providers - select your
  preferred provider for intelligent code review
- **Smart Blocking**: Blocks commits with critical issues (security
  vulnerabilities, dangerous operations, critical bugs)
- **Actionable Feedback**: Provides suggestions for non-critical improvements
  without blocking commits
- **Multi-file Support**: Handles multiple staged files in a single review
- **Configurable Ignore Patterns**: Exclude files from review using
  `.solventignore` (gitignore-style patterns)
- **File-Specific Context**: Provide custom AI context per file/directory using
  `.solventrules`
- **File Size Limits**: Automatically skips files larger than the configured
  limit (default: 1MB) to prevent API issues
- **BDD Testing**: Comprehensive test coverage using behave

## Installation

### From PyPI (Recommended)

Install Solvent from PyPI:

```bash
pip install solvent-ai
```

Or using `uv`:

```bash
uv pip install solvent-ai
```

### From Source

This project uses [uv](https://github.com/astral-sh/uv) for fast and reliable
dependency management.

```bash
# Clone the repository
git clone https://github.com/mbocevski/solvent.git
cd solvent

# Install dependencies
uv sync

# Install with dev dependencies (for development)
uv sync --group dev

# Install the package in development mode
uv pip install -e .
```

## Configuration

### Environment Variables

Solvent uses environment variables for configuration. All settings use the
`SOLVENT_` prefix and are case-insensitive.

**AI Provider Selection:**

```bash
export SOLVENT_AI_PROVIDER="provider-name"  # Select your preferred AI provider
```

**Configuration Options by Provider:**

| Provider      | Required Settings           | Optional Settings                                            | Defaults                                                         |
| ------------- | --------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------- |
| **gemini**    | `SOLVENT_GEMINI_API_KEY`    | `SOLVENT_GEMINI_MODEL`<br>`SOLVENT_GEMINI_TEMPERATURE`       | Model: `gemini-2.5-flash`<br>Temperature: `0.7`                  |
| **openai**    | `SOLVENT_OPENAI_API_KEY`    | `SOLVENT_OPENAI_MODEL`<br>`SOLVENT_OPENAI_TEMPERATURE`       | Model: `gpt-4o-mini`<br>Temperature: `0.7`                       |
| **anthropic** | `SOLVENT_ANTHROPIC_API_KEY` | `SOLVENT_ANTHROPIC_MODEL`<br>`SOLVENT_ANTHROPIC_TEMPERATURE` | Model: `claude-haiku-4-5`<br>Temperature: `0.7` (range: 0.0-1.0) |

**General Settings (apply to all providers):**

| Setting                 | Description                                                     | Default                       |
| ----------------------- | --------------------------------------------------------------- | ----------------------------- |
| `SOLVENT_MAX_TOKENS`    | Maximum output tokens for AI responses                          | Model limit (Anthropic: 4096) |
| `SOLVENT_LOG_LEVEL`     | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | `INFO`                        |
| `SOLVENT_MAX_FILE_SIZE` | Maximum file size in bytes to review                            | `1048576` (1MB)               |

**Example Configuration:**

```bash
# Select provider
export SOLVENT_AI_PROVIDER="gemini"

# Required: Provider API key
export SOLVENT_GEMINI_API_KEY="your-api-key-here"

# Optional: Provider-specific settings
export SOLVENT_GEMINI_MODEL="gemini-2.5-flash"
export SOLVENT_GEMINI_TEMPERATURE="0.7"

# Optional: General settings
export SOLVENT_MAX_TOKENS="4096"  # Limit response length for all providers
export SOLVENT_LOG_LEVEL="INFO"
export SOLVENT_MAX_FILE_SIZE="1048576"
```

> **Note**:
>
> - Temperature range: `0.0` to `2.0` for Gemini and OpenAI, `0.0` to `1.0` for
>   Anthropic
> - Each provider requires its own API key
> - Refer to your provider's documentation for available model options

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

After setting your API key and provider:

```bash
# Review staged files (uses provider from SOLVENT_AI_PROVIDER or defaults to gemini)
uv run solvent

# Or if installed globally
solvent
```

**Example:**

```bash
# Set your provider and corresponding API key
export SOLVENT_AI_PROVIDER="your-provider"
export SOLVENT_YOUR_PROVIDER_API_KEY="your-api-key"
uv run solvent
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
framework. Add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/mbocevski/solvent
    rev: v0.1.1 # Use a specific version tag
    hooks:
      - id: solvent
        verbose: true # Always show output to see the AI response when status Passed
```

Then install the hooks:

```bash
pre-commit install
```

The hook will automatically install Solvent and its dependencies when first run.

> **Note**: By default, pre-commit only shows output from hooks that fail. Add
> `verbose: true` to the hook configuration to always see AI feedback, even when
> the review passes. This is useful for seeing suggestions and improvements.

#### Alternative: Local Hook (For Development)

If you're developing Solvent or want to use a local installation:

```bash
# Install Solvent first
pip install solvent-ai
# Or: uv add solvent-ai
```

Then use a local hook in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: solvent
        name: Solvent AI Code Review
        entry: solvent # or: uv run solvent
        language: system
        pass_filenames: false
        always_run: true
```

> **Important**: Make sure to set the appropriate API key environment variable
> for your selected provider before running pre-commit hooks. You can set it in
> your shell profile or use a tool like `direnv` for project-specific
> environment variables.

## How It Works

Solvent follows a streamlined workflow to review your code:

1. **Detects Staged Files**: Scans the git repository for all files staged for
   commit
2. **Applies Ignore Patterns**: Filters out files matching `.solventignore`
   patterns (if present)
3. **Checks File Sizes**: Skips files larger than the configured size limit
   (default: 1MB) to prevent API token limits and timeouts
4. **Loads Context Rules**: Loads file-specific context from `.solventrules` (if
   present)
5. **Reads File Contents**: Reads the contents of non-ignored, size-appropriate
   staged files (skips binary files, files with encoding errors, and oversized
   files)
6. **AI Review**: Sends files to the configured AI provider for review,
   including file-specific context where applicable
7. **Determines Pass/Fail**: Analyzes AI feedback for critical issues using:
   - Machine-readable status block (preferred)
   - Keyword-based fallback detection
8. **Returns Result**: Returns `HookResult` with pass/fail status and detailed
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
# Set your provider and API key
export SOLVENT_AI_PROVIDER="your-provider"
export SOLVENT_YOUR_PROVIDER_API_KEY="your-api-key"

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
├── src/solvent_ai/
│   ├── __init__.py              # Main package exports
│   ├── main.py                  # CLI entry point
│   ├── hook/
│   │   ├── __init__.py          # Hook module exports
│   │   ├── orchestrator.py      # Pre-commit hook orchestration
│   │   └── evaluator.py         # Pass/fail evaluation logic
│   ├── ai/
│   │   ├── __init__.py          # AI module exports
│   │   ├── base.py              # Abstract base class for AI clients
│   │   ├── factory.py           # Factory for creating AI clients
│   │   ├── context.py           # AI prompt context and templates
│   │   ├── retry.py             # Retry logic for API calls
│   │   ├── gemini/              # Gemini provider implementation
│   │   │   ├── __init__.py
│   │   │   └── client.py
│   │   └── openai/              # OpenAI provider implementation
│   │       ├── __init__.py
│   │       └── client.py
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
- AI provider API key (Gemini or OpenAI) for running tests

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
- **AI Provider API Key**: Required for AI reviews (varies by provider)
- **Git Repository**: Solvent operates on git repositories
- **Dependencies**: Automatically installed via `uv sync`:
  - Provider-specific API clients (installed as needed)
  - `GitPython`: Git repository operations
  - `pydantic` / `pydantic-settings`: Configuration management
  - `pathspec`: Pattern matching for ignore/rules files

## Troubleshooting

### API Key Issues

**Error: "AI review authentication failed" or "API key not valid"**

- Ensure the appropriate API key is set in your environment for your selected
  provider
- Verify the API key is correct and not expired
- Check that the API key has the necessary permissions
- Refer to your provider's documentation for obtaining a new API key

**Error: "AI review permission denied"**

- Your API key may not have the required permissions
- Check your provider's account settings and ensure the API is enabled
- Verify API key permissions match the required access level

### Rate Limiting

**Error: "AI review service rate limit exceeded"**

- AI provider APIs have rate limits based on your usage tier
- Wait a few moments and try again
- Consider upgrading your API quota if you frequently hit limits
- The hook automatically retries with exponential backoff (up to 3 attempts)

### Service Unavailable

**Error: "AI review service is temporarily unavailable"**

- The AI provider service may be experiencing downtime
- The hook automatically retries transient errors (503, 502, 504)
- Wait a few moments and try again
- Check your provider's service status page for current status

### No Files to Review

**Message: "No staged files to review"**

- Ensure you have files staged with `git add`
- Run `git status` to verify staged files
- The hook only reviews files that are staged for commit

**Message: "All staged files are ignored"**

- Check your `.solventignore` file for patterns that might be too broad
- Verify the patterns match what you expect
- Files matching `.solventignore` patterns are excluded from review

**Message: "All staged files were skipped (too large, binary, or unreadable)"**

- Files larger than the configured size limit (default: 1MB) are skipped
- Binary files and files with encoding errors are skipped
- Adjust `SOLVENT_MAX_FILE_SIZE` if you need to review larger files
- Note: Very large files may hit API token limits

### Git Repository Issues

**Error: "Error accessing git repository"**

- Ensure you're running `solvent` from within a git repository
- Run `git status` to verify you're in a valid repository
- Check that `.git` directory exists and is accessible

### Configuration Issues

**Settings not being applied**

- Environment variables must use the `SOLVENT_` prefix
- Variable names are case-insensitive
- Restart your terminal/shell after setting environment variables
- Verify the variable is set:
  - For provider: `echo $SOLVENT_AI_PROVIDER`
  - For API key: `echo $SOLVENT_YOUR_PROVIDER_API_KEY` (replace with your
    provider's key variable)

**Log level not changing**

- Ensure `SOLVENT_LOG_LEVEL` is set to one of: `DEBUG`, `INFO`, `WARNING`,
  `ERROR`, `CRITICAL`
- Check that the variable is exported: `export SOLVENT_LOG_LEVEL=DEBUG`
- Run with `SOLVENT_LOG_LEVEL=DEBUG uv run solvent` to test

### File Reading Issues

**Files are being skipped unexpectedly**

- Check file encoding (only UTF-8 text files are reviewed)
- Verify file permissions (must be readable)
- Ensure files exist and are not symlinks to non-existent files
- Binary files are automatically skipped

### Getting More Information

**Enable debug logging:**

```bash
export SOLVENT_LOG_LEVEL=DEBUG
uv run solvent
```

This will show detailed information about:

- Which files are being reviewed
- Which files are being skipped and why
- API request/response details
- Retry attempts

**Check version:**

```bash
uv run solvent --version
```

**Get help:**

```bash
uv run solvent --help
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
