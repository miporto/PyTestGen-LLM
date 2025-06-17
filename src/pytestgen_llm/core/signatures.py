"""
DSPy signatures for test generation strategies.

This module defines the structured interfaces between the ensemble system and LLMs
for different test generation strategies. Each signature specifies the input/output
format and provides validation for the test generation process.
"""

import ast
import re
from typing import Any

import dspy
from pydantic import BaseModel, Field, field_validator


class SignatureValidationError(Exception):
    """Raised when signature input validation fails."""

    pass


class CodeInput(BaseModel):
    """Pydantic model for validating test code inputs."""

    code: str = Field(..., min_length=1, description="Python source code")
    file_type: str = Field(default="test", description="Type of code file")

    @field_validator("code")
    @classmethod
    def validate_python_syntax(cls, v: str) -> str:
        """Validate that the code has valid Python syntax."""
        try:
            ast.parse(v)
            return v
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")

    @field_validator("code")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure code is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        return v


class ExtendCoverageSignature(dspy.Signature):
    """
    Generate additional pytest test functions to increase test coverage.

    This signature focuses on identifying untested code paths and generating
    comprehensive test cases that improve overall test coverage, especially
    for corner cases and edge conditions that may have been missed.

    Strategy: Analyzes both the existing test class and the source code to
    identify gaps in coverage and generate targeted test cases.

    Use Cases:
    - When you have low test coverage and need systematic improvement
    - When existing tests miss important code paths
    - For comprehensive test suite enhancement
    """

    existing_test_class = dspy.InputField(
        desc=(
            "The complete source code of the existing pytest test class, "
            "including all current test methods, fixtures, and imports. "
            "This helps understand what is already being tested."
        )
    )

    class_under_test = dspy.InputField(
        desc=(
            "The complete source code of the class or module being tested. "
            "Include all methods, properties, and functionality that should "
            "be covered by tests. This is used to identify untested code paths."
        )
    )

    new_test_functions = dspy.OutputField(
        desc=(
            "A list of new, complete pytest test functions that improve coverage. "
            "Each function should be syntactically correct, properly named (test_*), "
            "include appropriate assertions, and target specific untested code paths. "
            "Focus on realistic scenarios and edge cases."
        )
    )


class CornerCasesSignature(dspy.Signature):
    """
    Generate pytest test functions targeting corner cases and edge conditions.

    This signature specializes in identifying and testing boundary conditions,
    error scenarios, and unusual input combinations that could cause failures
    in production but are often overlooked in basic testing.

    Strategy: Focuses specifically on edge cases like null values, empty
    collections, boundary values, error conditions, and exceptional scenarios.

    Use Cases:
    - When you need robust error handling coverage
    - For testing boundary conditions and edge cases
    - When preparing for production resilience
    """

    existing_test_class = dspy.InputField(
        desc=(
            "The complete source code of the existing pytest test class. "
            "Used to understand what corner cases are already being tested "
            "and avoid duplication."
        )
    )

    class_under_test = dspy.InputField(
        desc=(
            "The complete source code of the class or module being tested. "
            "Analyze for potential edge cases like null inputs, empty collections, "
            "boundary values, type mismatches, and error conditions."
        )
    )

    corner_case_tests = dspy.OutputField(
        desc=(
            "A list of pytest test functions specifically targeting corner cases. "
            "Focus on: null/None values, empty strings/lists/dicts, boundary values "
            "(min/max), invalid inputs, exception scenarios, race conditions, "
            "and unusual but valid input combinations. Each test should be complete "
            "and properly handle expected exceptions."
        )
    )


class ExtendTestSignature(dspy.Signature):
    """
    Generate additional pytest test functions based solely on test class analysis.

    This signature works with minimal context, analyzing only the existing test
    structure to infer what additional tests might be beneficial. Useful when
    source code access is limited or when extending test coverage based on
    testing patterns.

    Strategy: Infers missing test scenarios by analyzing the existing test
    structure, naming patterns, and tested scenarios.

    Use Cases:
    - When source code access is limited
    - For pattern-based test extension
    - When working with legacy or third-party code
    """

    existing_test_class = dspy.InputField(
        desc=(
            "The complete source code of the existing pytest test class. "
            "Analyze the structure, patterns, and existing test scenarios to "
            "infer what additional tests would be valuable. Look for gaps "
            "in the testing patterns and missing complementary test cases."
        )
    )

    extended_tests = dspy.OutputField(
        desc=(
            "A list of additional pytest test functions that complement the "
            "existing test suite. Base these on patterns observed in the existing "
            "tests, filling logical gaps and adding complementary scenarios. "
            "Each test should follow the existing naming and structure conventions."
        )
    )


class StatementCompleteSignature(dspy.Signature):
    """
    Complete test generation based on a specific completion prompt.

    This signature provides flexibility for custom test generation scenarios
    where specific guidance or context is needed beyond the standard patterns.
    It allows for targeted test generation with custom prompts.

    Strategy: Uses a completion-style approach where a specific prompt guides
    the test generation, allowing for highly targeted and contextual tests.

    Use Cases:
    - When you need specific types of tests (performance, integration, etc.)
    - For custom testing scenarios not covered by other signatures
    - When providing specific test generation guidance
    """

    existing_test_class = dspy.InputField(
        desc=(
            "The complete source code of the existing pytest test class. "
            "Provides context for the completion task."
        )
    )

    class_under_test = dspy.InputField(
        desc=(
            "The complete source code of the class or module being tested. "
            "Used as reference for generating the requested test types."
        )
    )

    completion_prompt = dspy.InputField(
        desc=(
            "Specific instructions or prompts for test generation. "
            "Examples: 'Generate integration tests', 'Focus on performance testing', "
            "'Test error handling scenarios', 'Create parameterized tests'. "
            "This guides the specific type and focus of generated tests."
        )
    )

    completed_tests = dspy.OutputField(
        desc=(
            "A list of pytest test functions that fulfill the completion prompt. "
            "Tests should directly address the specific requirements in the prompt "
            "while maintaining proper pytest structure and assertions."
        )
    )


def validate_signature_inputs(
    existing_test_class: str,
    class_under_test: str | None = None,
    completion_prompt: str | None = None,
) -> dict[str, Any]:
    """
    Validate inputs for DSPy signatures.

    Args:
        existing_test_class: The test class source code
        class_under_test: Optional source code of class being tested
        completion_prompt: Optional completion prompt

    Returns:
        Dict containing validated inputs

    Raises:
        SignatureValidationError: If validation fails
    """
    try:
        # Validate test class
        test_input = CodeInput(code=existing_test_class, file_type="test")

        # Validate that test class contains test functions
        if not re.search(r"def\s+test_\w+\s*\(", existing_test_class):
            raise SignatureValidationError(
                "Test class must contain at least one test function (def test_*)"
            )

        validated = {"existing_test_class": test_input.code}

        # Validate source class if provided
        if class_under_test:
            source_input = CodeInput(code=class_under_test, file_type="source")
            validated["class_under_test"] = source_input.code

        # Validate completion prompt if provided
        if completion_prompt:
            if not completion_prompt.strip():
                raise SignatureValidationError("Completion prompt cannot be empty")
            validated["completion_prompt"] = completion_prompt.strip()

        return validated

    except ValueError as e:
        raise SignatureValidationError(f"Input validation failed: {e}")


def parse_test_functions(generated_output: str) -> list[str]:
    """
    Parse and extract individual test functions from generated output.

    Args:
        generated_output: Raw output from LLM containing test functions

    Returns:
        List of individual test function strings

    Raises:
        SignatureValidationError: If no valid test functions found
    """
    if not generated_output or not generated_output.strip():
        raise SignatureValidationError("Generated output is empty")

    # Try to parse as Python to validate syntax
    try:
        tree = ast.parse(generated_output)
    except SyntaxError as e:
        raise SignatureValidationError(
            f"Generated output has invalid Python syntax: {e}"
        )

    # Extract test functions
    test_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            # Extract the function source code
            lines = generated_output.split("\n")
            start_line = node.lineno - 1

            # Find the end of the function
            end_line = start_line + 1
            while end_line < len(lines) and (
                lines[end_line].startswith("    ") or lines[end_line].strip() == ""
            ):
                end_line += 1

            func_code = "\n".join(lines[start_line:end_line])
            test_functions.append(func_code)

    if not test_functions:
        raise SignatureValidationError(
            "No valid test functions found in generated output"
        )

    return test_functions


def extract_test_name(test_function_code: str) -> str:
    """
    Extract the test function name from test code.

    Args:
        test_function_code: Source code of a test function

    Returns:
        The test function name

    Raises:
        SignatureValidationError: If function name cannot be extracted
    """
    match = re.search(r"def\s+(test_\w+)\s*\(", test_function_code)
    if not match:
        raise SignatureValidationError("Could not extract test function name")
    return match.group(1)


def normalize_test_code(test_code: str) -> str:
    """
    Normalize test code for comparison and duplicate detection.

    Args:
        test_code: Source code of a test function

    Returns:
        Normalized version of the test code
    """
    # Remove leading/trailing whitespace and normalize line endings
    normalized = test_code.strip().replace("\r\n", "\n").replace("\r", "\n")

    # Remove extra blank lines
    lines = [line.rstrip() for line in normalized.split("\n")]
    normalized_lines = []
    prev_blank = False

    for line in lines:
        if line == "":
            if not prev_blank:
                normalized_lines.append(line)
            prev_blank = True
        else:
            normalized_lines.append(line)
            prev_blank = False

    return "\n".join(normalized_lines)
