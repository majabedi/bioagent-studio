from __future__ import annotations


class AppError(Exception):
    """Base application error."""


class ConfigError(AppError):
    """Configuration or environment error."""


class LLMError(AppError):
    """Errors returned by the LLM client."""


class SpecificationError(AppError):
    """Model specification validation failed."""


class SimulationSizeError(AppError):
    """A simulation size limit was exceeded."""


class SimulationError(AppError):
    """A simulation execution error."""


class UnsupportedRuleError(AppError):
    """A biological rule could not be mapped to the controlled engine."""
