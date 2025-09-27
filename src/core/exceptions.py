"""Custom exceptions for the dashboard."""

from __future__ import annotations


class DashboardError(Exception):
    """Base exception for dashboard errors."""
    pass


class DataLoadError(DashboardError):
    """Raised when data cannot be loaded."""
    pass


class DataValidationError(DashboardError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(DashboardError):
    """Raised when configuration is invalid."""
    pass