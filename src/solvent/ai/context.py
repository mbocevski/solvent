"""Prompt context and templates for AI code review."""

import textwrap


def build_pre_commit_review_prompt(file_contents: dict[str, str]) -> str:
    """Build the prompt for reviewing staged files in a pre-commit hook.

    Args:
        file_contents: Dictionary mapping file paths to their contents.

    Returns:
        Formatted prompt string with context and file contents.
    """
    prompt = _get_pre_commit_context()

    prompt += "STAGED FILES TO REVIEW:\n" + "=" * 80 + "\n\n"

    for file_path, content in file_contents.items():
        prompt += f"File: {file_path}\n"
        prompt += "-" * 80 + "\n"
        prompt += content
        prompt += "\n" + "-" * 80 + "\n\n"

    prompt += _get_review_format_instructions()

    return prompt


def _get_pre_commit_context() -> str:
    """Get the context section explaining the pre-commit hook scenario.

    Returns:
        Context string explaining the pre-commit hook system.
    """
    return textwrap.dedent(
        """\
        You are an expert code reviewer working as part of a pre-commit hook system.

        CONTEXT:
        - This is a pre-commit hook that runs automatically before code is committed
          to a git repository
        - The files below are currently STAGED and about to be committed
        - Your review will determine whether this commit is ALLOWED or BLOCKED
        - If you identify CRITICAL issues, the commit will be blocked and the
          developer must fix them
        - If you only find minor issues or suggestions, the commit will proceed
        - Only successfully readable text files are included in this review
          (binary files and files with encoding errors are excluded)

        YOUR ROLE:
        Review the staged files and provide a comprehensive code review that helps
        maintain code quality and security while being practical about what truly
        needs to block a commit.

        CRITICAL ISSUES (MUST BLOCK COMMIT):
        These are serious problems that MUST prevent the commit from proceeding:
        - Security vulnerabilities (SQL injection, XSS, code injection, remote code
          execution, etc.)
        - Dangerous operations (unintended file deletion, system command execution,
          etc.)
        - Critical bugs that could cause data loss, system failures, or production
          outages
        - Unsafe code patterns that introduce significant risk
        - Hardcoded secrets, credentials, or sensitive information
        - Code that violates critical business logic or safety requirements

        NON-CRITICAL ISSUES (SUGGESTIONS ONLY):
        These should be mentioned but should NOT block the commit:
        - Code style violations (formatting, naming conventions, etc.)
        - Minor code quality improvements (refactoring opportunities, etc.)
        - Performance optimizations that don't affect correctness
        - Documentation improvements
        - Best practice suggestions that don't introduce immediate risk

        IMPORTANT INSTRUCTIONS:
        - Be clear and explicit when identifying CRITICAL issues - use words like
          'CRITICAL', 'MUST FIX', 'BLOCKING', 'SECURITY VULNERABILITY', 'DANGEROUS',
          etc.
        - For non-critical issues, use softer language like 'consider', 'suggestion',
          'improvement', etc.
        - Your feedback will be analyzed by keyword detection, so be explicit about
          severity
        - Focus on issues that matter NOW, not theoretical future problems
        - Consider the context: is this a critical production system or a
          development script?

        """
    )


def _get_review_format_instructions() -> str:
    """Get the review format instructions section.

    Returns:
        Review format instructions string.
    """
    return textwrap.dedent(
        """\
        ================================================================================

        REVIEW FORMAT:
        IMPORTANT: Start your response with a machine-readable status block that will
        be parsed automatically. Use this EXACT format:

        ---BEGIN STATUS---
        STATUS: PASS|FAIL
        CRITICAL_ISSUES_COUNT: <number>
        ---END STATUS---

        Where:
        - STATUS: Use "PASS" if no critical issues found, "FAIL" if critical
          issues exist
        - CRITICAL_ISSUES_COUNT: Number of critical issues (0 if STATUS is PASS)

        After the status block, provide your detailed review:

        1. OVERALL ASSESSMENT
           - Brief summary of the changes
           - General code quality assessment

        2. CRITICAL ISSUES (BLOCKING)
           - List any CRITICAL issues that MUST block this commit
           - Be explicit: use words like 'CRITICAL', 'MUST FIX', 'BLOCKING',
             'SECURITY VULNERABILITY'
           - If no critical issues, simply state: 'No critical issues found'
             Do NOT add explanations, clarifications, or context about why
             something is not a critical issue. Keep it brief and factual.

        3. SUGGESTIONS (NON-BLOCKING)
           - Code improvements, style suggestions, best practices
           - These will NOT block the commit but are helpful for future iterations

        4. POSITIVE ASPECTS (OPTIONAL)
           - What was done well, good patterns, etc.

        Remember: Only CRITICAL issues should block the commit. Everything else
        should be suggestions. The STATUS block at the top is critical for automated
        processing.
        """
    )
