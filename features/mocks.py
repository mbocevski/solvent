"""Mock responses for Gemini API in behave tests."""

import os

# Mock responses that match the expected format with status blocks


def _build_mock_response_pass(file_contents: dict[str, str]) -> str:
    """Build a PASS mock response matching real Gemini API format."""
    file_names = ", ".join([os.path.basename(f) for f in file_contents])
    return f"""---BEGIN STATUS---
STATUS: PASS
CRITICAL_ISSUES_COUNT: 0
---END STATUS---

1.  **OVERALL ASSESSMENT**
    The staged file(s) {file_names} contain well-structured code with good
    practices. Overall, the code quality is high.

2.  **CRITICAL ISSUES (BLOCKING)**
    No critical issues found.

3.  **SUGGESTIONS (NON-BLOCKING)**
    *   No significant suggestions for improvement. The code is clean and
        follows good practices.

4.  **POSITIVE ASPECTS (OPTIONAL)**
    *   **Clear Functionality**: Functions are well-defined and perform their
        intended tasks clearly.
    *   **Type Hinting**: Excellent use of type hints enhances readability and
        maintainability.
    *   **Docstrings**: Comprehensive docstrings are provided, aiding
        understanding.
    *   **Readability**: The code is highly readable and follows standard
        Python conventions.
"""


MOCK_RESPONSE_PASS = """---BEGIN STATUS---
STATUS: PASS
CRITICAL_ISSUES_COUNT: 0
---END STATUS---

## Review Summary

The code looks good overall. No critical issues were found.

## Suggestions

- Consider adding more comprehensive error handling
- Some functions could benefit from additional type hints
"""

MOCK_RESPONSE_FAIL = """---BEGIN STATUS---
STATUS: FAIL
CRITICAL_ISSUES_COUNT: 4
---END STATUS---

1.  **OVERALL ASSESSMENT**
    This commit includes files with severe security vulnerabilities and
    dangerous operations that **MUST BLOCK** this commit.

2.  **CRITICAL ISSUES (BLOCKING)**
    The following CRITICAL issues were identified and **MUST BLOCK** this
    commit:

    *   **CRITICAL: Hardcoded Secret**: Variables contain hardcoded sensitive
        secrets (passwords, API keys). This is a **SECURITY VULNERABILITY**.
        Secrets should be loaded from environment variables or a secure secret
        management system, not committed to source control. **MUST FIX**.
    *   **CRITICAL: Remote Code Execution**: The `eval(input("Enter code: "))`
        statement allows arbitrary code execution by anyone providing input.
        This is a severe **SECURITY VULNERABILITY** and a **DANGEROUS
        OPERATION** that can lead to system compromise. **MUST FIX**.
    *   **CRITICAL: Dangerous System Command Execution**: The
        `os.system("rm -rf /")` command is an extremely **DANGEROUS OPERATION**
        that attempts to recursively delete the root directory. This could
        lead to catastrophic data loss and system failure. This code **MUST
        NOT** be committed. **MUST FIX**.
    *   **CRITICAL: SQL Injection Vulnerability**: SQL queries directly
        interpolate user input into the query string. This is a classic
        **SECURITY VULNERABILITY** for SQL injection, allowing malicious input
        to alter the query's intent. Parameterized queries or ORMs should be
        used to prevent this. **MUST FIX**.

3.  **SUGGESTIONS (NON-BLOCKING)**
    *   These issues must be addressed before committing.

4.  **POSITIVE ASPECTS (OPTIONAL)**
    *   N/A - Critical issues must be resolved first.
"""

MOCK_RESPONSE_MINOR_ISSUES = """---BEGIN STATUS---
STATUS: PASS
CRITICAL_ISSUES_COUNT: 0
---END STATUS---

## Review Summary

No critical issues found. The code is functional but could be improved.

## Suggestions

1. **Type Hints**: Consider adding type hints to function parameters and
   return values for better code clarity and IDE support.
2. **Documentation**: Add docstrings to functions to explain their purpose,
   parameters, and return values.
3. **Code Quality**: The function could benefit from more descriptive
   variable names.

These are suggestions for improvement but do not block the commit.
"""

MOCK_RESPONSE_WITH_CONTEXT = """---BEGIN STATUS---
STATUS: PASS
CRITICAL_ISSUES_COUNT: 0
---END STATUS---

## Review Summary

Reviewing with provided context: This is test code. Focus on test quality,
coverage, edge cases, and correctness.

The test code looks appropriate for its purpose. No critical issues found.

## Suggestions

- Consider adding edge case tests
- Ensure good test coverage
"""


def get_mock_response_for_scenario(
    scenario_name: str, file_contents: dict[str, str]
) -> str:
    """Get appropriate mock response based on scenario and file contents.

    Args:
        scenario_name: Name of the behave scenario.
        file_contents: Dictionary of file paths to contents (for context).

    Returns:
        Mock API response string.
    """
    # Check file contents for problematic patterns
    all_content = " ".join(file_contents.values()).lower()

    # Determine response based on content
    if any(
        keyword in all_content
        for keyword in ["eval(", "os.system", "password =", "secret", "rm -rf"]
    ):
        return MOCK_RESPONSE_FAIL

    # Check for minor issues
    if "def func(" in all_content and "->" not in all_content:
        # Missing type hints - include file names
        file_names = ", ".join([os.path.basename(f) for f in file_contents])
        return f"""---BEGIN STATUS---
STATUS: PASS
CRITICAL_ISSUES_COUNT: 0
---END STATUS---

1.  **OVERALL ASSESSMENT**
    This commit introduces a new Python file(s) {file_names} containing
    simple functions. The changes are minor, adding basic functionality. The
    general code quality is clear and readable, but there are opportunities for
    improvement regarding documentation, type hinting, and minor code style.

2.  **CRITICAL ISSUES (BLOCKING)**
    No critical issues found.

3.  **SUGGESTIONS (NON-BLOCKING)**
    *   **Type Hints:** Consider adding type hints to function parameters and
        return values for better readability, maintainability, and static
        analysis. For example: `def func(x: int) -> int:`.
    *   **Docstring:** Consider adding a docstring to explain what the
        function does, its parameters, and what it returns.
    *   **List Comprehension:** The `for` loop can be more concisely
        expressed using a list comprehension for more Pythonic and readable
        code.

4.  **POSITIVE ASPECTS (OPTIONAL)**
    *   The code is straightforward and easy to understand.
    *   The function names are descriptive.
"""

    # Check if context rules were provided (indicated by test context)
    if "test" in scenario_name.lower() or any(
        "test" in path.lower() for path in file_contents
    ):
        file_names = ", ".join([os.path.basename(f) for f in file_contents])
        return f"""---BEGIN STATUS---
STATUS: PASS
CRITICAL_ISSUES_COUNT: 0
---END STATUS---

1.  **OVERALL ASSESSMENT**
    Reviewing with provided context: This is test code. Focus on test
    quality, coverage, edge cases, and correctness. The staged file(s)
    {file_names} contain test code that is appropriate for its purpose.

2.  **CRITICAL ISSUES (BLOCKING)**
    No critical issues found.

3.  **SUGGESTIONS (NON-BLOCKING)**
    *   Consider adding edge case tests for better coverage.
    *   Ensure good test coverage of all code paths.

4.  **POSITIVE ASPECTS (OPTIONAL)**
    *   The test code follows appropriate testing patterns.
    *   Test scenarios are well-structured.
"""

    # Default to pass - include file names
    return _build_mock_response_pass(file_contents)
