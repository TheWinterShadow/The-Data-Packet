"""Configuration-related exceptions."""


class ConfigurationError(Exception):
    """Raised when there's an issue with configuration."""

    pass


class MissingAPIKeyError(ConfigurationError):
    """Raised when a required API key is missing."""

    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid."""

    pass
