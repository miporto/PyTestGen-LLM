"""
Comprehensive tests for DSPy signature definitions and validation.
"""

import ast
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

import dspy
from pytestgen_llm.core.signatures import (
    ExtendCoverageSignature,
    CornerCasesSignature,
    ExtendTestSignature,
    StatementCompleteSignature,
    SignatureValidationError,
    CodeInput,
    validate_signature_inputs,
    parse_test_functions,
    extract_test_name,
    normalize_test_code,
)


class TestSignatureClasses:
    """Test that all signature classes are properly defined."""
    
    def test_extend_coverage_signature_inheritance(self):
        """Test ExtendCoverageSignature inherits from dspy.Signature."""
        assert issubclass(ExtendCoverageSignature, dspy.Signature)
    
    def test_corner_cases_signature_inheritance(self):
        """Test CornerCasesSignature inherits from dspy.Signature."""
        assert issubclass(CornerCasesSignature, dspy.Signature)
    
    def test_extend_test_signature_inheritance(self):
        """Test ExtendTestSignature inherits from dspy.Signature."""
        assert issubclass(ExtendTestSignature, dspy.Signature)
    
    def test_statement_complete_signature_inheritance(self):
        """Test StatementCompleteSignature inherits from dspy.Signature."""
        assert issubclass(StatementCompleteSignature, dspy.Signature)
    
    def test_extend_coverage_signature_structure(self):
        """Test ExtendCoverageSignature has correct structure."""
        # Test that the signature can be instantiated and has the expected behavior
        sig = ExtendCoverageSignature
        assert sig.__name__ == "ExtendCoverageSignature"
        assert hasattr(sig, '__doc__')
        assert "coverage" in sig.__doc__.lower()
    
    def test_corner_cases_signature_structure(self):
        """Test CornerCasesSignature has correct structure."""
        sig = CornerCasesSignature
        assert sig.__name__ == "CornerCasesSignature"
        assert hasattr(sig, '__doc__')
        assert "corner" in sig.__doc__.lower()
    
    def test_extend_test_signature_structure(self):
        """Test ExtendTestSignature has correct structure."""
        sig = ExtendTestSignature
        assert sig.__name__ == "ExtendTestSignature"
        assert hasattr(sig, '__doc__')
        assert "extend" in sig.__doc__.lower()
    
    def test_statement_complete_signature_structure(self):
        """Test StatementCompleteSignature has correct structure."""
        sig = StatementCompleteSignature
        assert sig.__name__ == "StatementCompleteSignature"
        assert hasattr(sig, '__doc__')
        assert "complete" in sig.__doc__.lower()


class TestCodeInputModel:
    """Test the Pydantic validation model."""
    
    def test_valid_code_input(self):
        """Test valid Python code passes validation."""
        valid_code = """
def test_example():
    assert True
        """
        
        input_model = CodeInput(code=valid_code)
        assert input_model.code == valid_code
        assert input_model.file_type == "test"
    
    def test_invalid_syntax_raises_error(self):
        """Test invalid Python syntax raises validation error."""
        invalid_code = """
def test_invalid(:
    assert True
        """
        
        with pytest.raises(ValueError, match="Invalid Python syntax"):
            CodeInput(code=invalid_code)
    
    def test_empty_code_raises_error(self):
        """Test empty code raises validation error."""
        with pytest.raises(ValidationError):
            CodeInput(code="")
    
    def test_whitespace_only_raises_error(self):
        """Test whitespace-only code raises validation error."""
        with pytest.raises(ValueError, match="Code cannot be empty"):
            CodeInput(code="   \n  \t  ")
    
    def test_custom_file_type(self):
        """Test custom file type is preserved."""
        valid_code = "def function(): pass"
        input_model = CodeInput(code=valid_code, file_type="source")
        assert input_model.file_type == "source"


class TestValidateSignatureInputs:
    """Test the signature input validation function."""
    
    @pytest.fixture
    def valid_test_class(self):
        """Fixture providing valid test class code."""
        return """
import pytest

class TestExample:
    def test_basic_functionality(self):
        assert True
        
    def test_edge_case(self):
        assert 1 + 1 == 2
        """
    
    @pytest.fixture
    def valid_source_class(self):
        """Fixture providing valid source class code."""
        return """
class Calculator:
    def add(self, a, b):
        return a + b
        
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
        """
    
    def test_valid_inputs_with_source_class(self, valid_test_class, valid_source_class):
        """Test validation passes with valid inputs including source class."""
        result = validate_signature_inputs(
            existing_test_class=valid_test_class,
            class_under_test=valid_source_class
        )
        
        assert "existing_test_class" in result
        assert "class_under_test" in result
        assert result["existing_test_class"] == valid_test_class
        assert result["class_under_test"] == valid_source_class
    
    def test_valid_inputs_without_source_class(self, valid_test_class):
        """Test validation passes with valid inputs without source class."""
        result = validate_signature_inputs(existing_test_class=valid_test_class)
        
        assert "existing_test_class" in result
        assert "class_under_test" not in result
        assert result["existing_test_class"] == valid_test_class
    
    def test_valid_inputs_with_completion_prompt(self, valid_test_class, valid_source_class):
        """Test validation passes with completion prompt."""
        prompt = "Generate performance tests"
        result = validate_signature_inputs(
            existing_test_class=valid_test_class,
            class_under_test=valid_source_class,
            completion_prompt=prompt
        )
        
        assert "completion_prompt" in result
        assert result["completion_prompt"] == prompt
    
    def test_invalid_test_class_syntax(self):
        """Test validation fails with invalid test class syntax."""
        invalid_code = "def invalid_syntax(:"
        
        with pytest.raises(SignatureValidationError, match="Input validation failed"):
            validate_signature_inputs(existing_test_class=invalid_code)
    
    def test_test_class_without_test_functions(self):
        """Test validation fails when test class has no test functions."""
        code_without_tests = """
class TestExample:
    def setup_method(self):
        pass
        
    def helper_function(self):
        return True
        """
        
        with pytest.raises(SignatureValidationError, match="must contain at least one test function"):
            validate_signature_inputs(existing_test_class=code_without_tests)
    
    def test_invalid_source_class_syntax(self, valid_test_class):
        """Test validation fails with invalid source class syntax."""
        invalid_source = "class Invalid(:"
        
        with pytest.raises(SignatureValidationError, match="Input validation failed"):
            validate_signature_inputs(
                existing_test_class=valid_test_class,
                class_under_test=invalid_source
            )
    
    def test_empty_completion_prompt(self, valid_test_class):
        """Test validation fails with empty completion prompt."""
        with pytest.raises(SignatureValidationError, match="Completion prompt cannot be empty"):
            validate_signature_inputs(
                existing_test_class=valid_test_class,
                completion_prompt="   "
            )


class TestParseTestFunctions:
    """Test the test function parsing utility."""
    
    def test_parse_single_test_function(self):
        """Test parsing a single test function."""
        generated_output = """
def test_example():
    assert True
        """
        
        result = parse_test_functions(generated_output)
        assert len(result) == 1
        assert "def test_example():" in result[0]
        assert "assert True" in result[0]
    
    def test_parse_multiple_test_functions(self):
        """Test parsing multiple test functions."""
        generated_output = """
def test_first():
    assert 1 == 1

def test_second():
    assert 2 == 2
    
def helper_function():
    return True

def test_third():
    assert helper_function()
        """
        
        result = parse_test_functions(generated_output)
        assert len(result) == 3
        
        # Check that only test functions are extracted
        test_names = [extract_test_name(func) for func in result]
        assert "test_first" in test_names
        assert "test_second" in test_names
        assert "test_third" in test_names
    
    def test_parse_empty_output_raises_error(self):
        """Test parsing empty output raises error."""
        with pytest.raises(SignatureValidationError, match="Generated output is empty"):
            parse_test_functions("")
    
    def test_parse_invalid_syntax_raises_error(self):
        """Test parsing invalid syntax raises error."""
        invalid_output = """
def test_invalid(:
    assert True
        """
        
        with pytest.raises(SignatureValidationError, match="invalid Python syntax"):
            parse_test_functions(invalid_output)
    
    def test_parse_no_test_functions_raises_error(self):
        """Test parsing code without test functions raises error."""
        no_tests_output = """
def helper_function():
    return True
    
class NotATest:
    pass
        """
        
        with pytest.raises(SignatureValidationError, match="No valid test functions found"):
            parse_test_functions(no_tests_output)
    
    def test_parse_complex_test_function(self):
        """Test parsing a complex test function with multiple lines."""
        complex_output = """
def test_complex_scenario():
    # Setup
    calculator = Calculator()
    test_data = [1, 2, 3, 4, 5]
    
    # Execute
    results = []
    for data in test_data:
        result = calculator.add(data, 10)
        results.append(result)
    
    # Assert
    expected = [11, 12, 13, 14, 15]
    assert results == expected
        """
        
        result = parse_test_functions(complex_output)
        assert len(result) == 1
        assert "def test_complex_scenario():" in result[0]
        assert "calculator = Calculator()" in result[0]
        assert "assert results == expected" in result[0]


class TestExtractTestName:
    """Test the test name extraction utility."""
    
    def test_extract_simple_test_name(self):
        """Test extracting name from simple test function."""
        test_code = """
def test_example():
    assert True
        """
        
        result = extract_test_name(test_code)
        assert result == "test_example"
    
    def test_extract_test_name_with_parameters(self):
        """Test extracting name from test function with parameters."""
        test_code = """
def test_with_params(self, mock_data):
    assert mock_data is not None
        """
        
        result = extract_test_name(test_code)
        assert result == "test_with_params"
    
    def test_extract_test_name_with_decorators(self):
        """Test extracting name from decorated test function."""
        test_code = """
@pytest.mark.parametrize("input,expected", [(1, 2), (2, 3)])
def test_parametrized(input, expected):
    assert input + 1 == expected
        """
        
        result = extract_test_name(test_code)
        assert result == "test_parametrized"
    
    def test_extract_test_name_invalid_function(self):
        """Test error when no test function found."""
        invalid_code = """
def helper_function():
    return True
        """
        
        with pytest.raises(SignatureValidationError, match="Could not extract test function name"):
            extract_test_name(invalid_code)


class TestNormalizeTestCode:
    """Test the test code normalization utility."""
    
    def test_normalize_removes_extra_whitespace(self):
        """Test normalization removes extra whitespace."""
        messy_code = """  
        
def test_example():
    assert True
    
    
        """
        
        result = normalize_test_code(messy_code)
        assert not result.startswith(" ")
        assert not result.endswith(" ")
        assert "\n\n\n" not in result
    
    def test_normalize_handles_different_line_endings(self):
        """Test normalization handles different line endings."""
        windows_code = "def test_example():\r\n    assert True\r\n"
        mac_code = "def test_example():\r    assert True\r"
        unix_code = "def test_example():\n    assert True\n"
        
        windows_result = normalize_test_code(windows_code)
        mac_result = normalize_test_code(mac_code)
        unix_result = normalize_test_code(unix_code)
        
        # All should normalize to the same format
        assert windows_result == mac_result == unix_result
        assert "\r" not in windows_result
    
    def test_normalize_preserves_indentation(self):
        """Test normalization preserves proper indentation."""
        indented_code = """
def test_example():
    if True:
        assert True
    else:
        assert False
        """
        
        result = normalize_test_code(indented_code)
        lines = result.split('\n')
        
        # Check indentation is preserved - find the function definition line
        func_line_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('def test_example():'):
                func_line_idx = i
                break
        
        assert func_line_idx is not None
        assert lines[func_line_idx + 1].startswith('    if True:')
        assert lines[func_line_idx + 2].startswith('        assert True')
    
    def test_normalize_removes_trailing_spaces(self):
        """Test normalization removes trailing spaces from lines."""
        code_with_trailing = "def test_example():   \n    assert True  \n"
        
        result = normalize_test_code(code_with_trailing)
        lines = result.split('\n')
        
        for line in lines:
            if line:  # Skip empty lines
                assert not line.endswith(' ')
                assert not line.endswith('\t')


class TestSignatureIntegration:
    """Integration tests for DSPy signature functionality."""
    
    @pytest.fixture
    def mock_dspy_predict(self):
        """Mock DSPy Predict for testing."""
        with patch('dspy.Predict') as mock:
            yield mock
    
    def test_signature_can_be_used_with_dspy_predict(self, mock_dspy_predict):
        """Test that signatures can be used with dspy.Predict."""
        # This tests the integration with DSPy framework
        predictor = dspy.Predict(ExtendCoverageSignature)
        assert predictor is not None
        
        # Verify mock was called with our signature
        mock_dspy_predict.assert_called_with(ExtendCoverageSignature)
    
    def test_all_signatures_work_with_dspy_predict(self, mock_dspy_predict):
        """Test all signatures can be instantiated with dspy.Predict."""
        signatures = [
            ExtendCoverageSignature,
            CornerCasesSignature,
            ExtendTestSignature,
            StatementCompleteSignature
        ]
        
        for signature in signatures:
            predictor = dspy.Predict(signature)
            assert predictor is not None


@pytest.fixture
def sample_test_class():
    """Fixture providing a sample test class for testing."""
    return """
import pytest
from calculator import Calculator

class TestCalculator:
    def setup_method(self):
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        result = self.calc.add(2, 3)
        assert result == 5
    
    def test_add_negative_numbers(self):
        result = self.calc.add(-2, -3)
        assert result == -5
    """


@pytest.fixture
def sample_source_class():
    """Fixture providing a sample source class for testing."""
    return """
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        return result
    
    def subtract(self, a, b):
        result = a - b
        self.history.append(f"subtract({a}, {b}) = {result}")
        return result
    
    def get_history(self):
        return self.history.copy()
    
    def clear_history(self):
        self.history.clear()
    """


class TestSignatureValidationIntegration:
    """Integration tests using sample fixtures."""
    
    def test_validate_with_fixtures(self, sample_test_class, sample_source_class):
        """Test validation works with realistic code samples."""
        result = validate_signature_inputs(
            existing_test_class=sample_test_class,
            class_under_test=sample_source_class,
            completion_prompt="Generate edge case tests"
        )
        
        assert "existing_test_class" in result
        assert "class_under_test" in result
        assert "completion_prompt" in result
        assert result["completion_prompt"] == "Generate edge case tests"
    
    def test_parse_realistic_test_output(self):
        """Test parsing realistic test function output."""
        realistic_output = """
def test_calculator_divide_by_zero(self):
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        self.calc.divide(10, 0)

def test_calculator_history_tracking(self):
    self.calc.add(1, 2)
    self.calc.subtract(5, 3)
    
    history = self.calc.get_history()
    assert len(history) == 2
    assert "add(1, 2) = 3" in history
    assert "subtract(5, 3) = 2" in history

def test_calculator_clear_history(self):
    self.calc.add(1, 1)
    assert len(self.calc.get_history()) == 1
    
    self.calc.clear_history()
    assert len(self.calc.get_history()) == 0
        """
        
        result = parse_test_functions(realistic_output)
        assert len(result) == 3
        
        names = [extract_test_name(func) for func in result]
        expected_names = [
            "test_calculator_divide_by_zero",
            "test_calculator_history_tracking", 
            "test_calculator_clear_history"
        ]
        
        for name in expected_names:
            assert name in names
