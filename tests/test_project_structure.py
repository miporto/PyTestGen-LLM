"""
Test project structure validation.
"""

from pathlib import Path

import pytest


def test_package_structure():
    """Test that the main package structure exists."""
    src_dir = Path("src/pytestgen_llm")
    assert src_dir.exists()

    # Check main package
    assert (src_dir / "__init__.py").exists()

    # Check subdirectories
    expected_dirs = ["core", "filters", "cli", "utils", "telemetry"]
    for dirname in expected_dirs:
        dir_path = src_dir / dirname
        assert dir_path.exists(), f"Directory {dirname} should exist"
        assert (dir_path / "__init__.py").exists(), f"Directory {dirname} should have __init__.py"


def test_main_package_imports():
    """Test that main package can be imported."""
    import pytestgen_llm

    # Check version attribute
    assert hasattr(pytestgen_llm, "__version__")
    assert isinstance(pytestgen_llm.__version__, str)

    # Check main function exists
    assert hasattr(pytestgen_llm, "main")


def test_cli_entry_point():
    """Test that CLI entry point can be imported."""
    try:
        from pytestgen_llm.cli.main import main
        assert callable(main)
    except ImportError as e:
        pytest.skip(f"CLI not yet implemented: {e}")


def test_core_modules():
    """Test that core modules can be imported."""
    try:
        from pytestgen_llm.core import TestGenEnsemble  # noqa: F401
        # This will fail until we implement the classes, which is expected
    except ImportError as e:
        pytest.skip(f"Core modules not yet implemented: {e}")


def test_test_structure():
    """Test that test directory structure is correct."""
    tests_dir = Path("tests")
    assert tests_dir.exists()

    # Check test subdirectories
    expected_test_dirs = ["unit", "integration", "fixtures"]
    for dirname in expected_test_dirs:
        dir_path = tests_dir / dirname
        assert dir_path.exists(), f"Test directory {dirname} should exist"
        assert (dir_path / "__init__.py").exists(), f"Test directory {dirname} should have __init__.py"
