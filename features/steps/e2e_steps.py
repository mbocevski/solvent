"""Step definitions for end-to-end integration tests."""

import os
import pathlib

from behave import given

# Reuse common steps from git_commit_review_steps
# Only define e2e-specific steps here


@given('the AI provider is set to "{provider}"')
def step_given_ai_provider(context, provider):
    """Set the AI provider environment variable."""
    os.environ["SOLVENT_AI_PROVIDER"] = provider


@given("I have staged files with good code for e2e")
def step_given_staged_good_code_e2e(context):
    """Create and stage files with good code for e2e testing."""
    # Create a well-written Python file
    test_file = os.path.join(context.temp_dir, "good_code_e2e.py")
    pathlib.Path(test_file).write_text(
        """\"\"\"A well-written Python module for e2e testing.\"\"\"

def calculate_sum(numbers: list[int]) -> int:
    \"\"\"Calculate the sum of a list of numbers.

    Args:
        numbers: List of integers to sum.

    Returns:
        The sum of all numbers in the list.
    \"\"\"
    return sum(numbers)


def process_data(data: dict[str, str]) -> list[str]:
    \"\"\"Process data dictionary into a list.

    Args:
        data: Dictionary with string keys and values.

    Returns:
        List of processed values.
    \"\"\"
    return [value.upper() for value in data.values()]


if __name__ == "__main__":
    result = calculate_sum([1, 2, 3, 4, 5])
    print(f"Sum: {result}")
""",
        encoding="utf-8",
    )

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]


@given("I have staged files with problematic code for e2e")
def step_given_staged_problematic_code_e2e(context):
    """Create and stage files with problematic code for e2e testing."""
    # Create a file with obvious issues
    test_file = os.path.join(context.temp_dir, "bad_code_e2e.py")
    pathlib.Path(test_file).write_text(
        """import os

# Hardcoded secret
password = "secret123"
api_key = "sk-1234567890abcdef"

# Dangerous operations
eval(input("Enter code: "))
os.system("rm -rf /")

# SQL injection risk
query = f"SELECT * FROM users WHERE id = {user_id}"
""",
        encoding="utf-8",
    )

    context.git_repo.index.add([test_file])
    context.staged_files = [test_file]


# All other steps are reused from git_commit_review_steps.py
# This file only contains e2e-specific step definitions
