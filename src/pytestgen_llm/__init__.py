"""
PyTestGen-LLM: Local Unit Test Improver using DSPy and Ensemble LLM Strategies

A powerful command-line tool that leverages LLMs to automatically and reliably
improve existing Python unit tests using ensemble learning and rigorous filtration.
"""

__version__ = "0.1.0"
__author__ = "Manuel Porto"
__email__ = "manuel@example.com"

from .cli.main import main
from .core import TestGenEnsemble

__all__ = ["TestGenEnsemble", "main", "__version__"]
