"""Enterprise Spec Framework exception hierarchy."""

from __future__ import annotations


class FrameworkError(Exception):
    """Base exception for Enterprise Spec Framework runtime errors."""


class ConfigurationError(FrameworkError):
    """Raised for malformed or incompatible framework configuration."""


class ContextError(FrameworkError):
    """Raised for context discovery or loading errors."""


class RuleCatalogError(FrameworkError):
    """Raised for rule catalog discovery or loading errors."""


class ValidationError(FrameworkError):
    """Raised for validator orchestration errors."""


class EngineError(FrameworkError):
    """Raised for governance engine execution errors."""

