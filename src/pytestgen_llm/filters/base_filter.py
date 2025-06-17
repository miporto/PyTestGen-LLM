"""
Base filter class for the filtration pipeline (stub implementation).
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseFilter(ABC):
    """
    Abstract base class for all filtration pipeline filters.

    This is a stub implementation that will be fully developed in Task 1.4.
    """

    @abstractmethod
    def filter(self, candidate_test: str) -> Any | None:
        """
        Apply this filter to a candidate test case.

        Args:
            candidate_test: The test case code to validate

        Returns:
            The test case if it passes the filter, None if it fails
        """
        pass

    @abstractmethod
    def get_filter_name(self) -> str:
        """Return the name of this filter for logging purposes."""
        pass
