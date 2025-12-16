"""Custom exceptions for The Data Packet."""


class TheDataPacketError(Exception):
    """Base exception for all The Data Packet errors."""

    pass


class ConfigurationError(TheDataPacketError):
    """Raised when there's an issue with configuration."""

    pass


class NetworkError(TheDataPacketError):
    """Raised when there's a network-related error."""

    pass


class ScrapingError(TheDataPacketError):
    """Raised when article scraping fails."""

    pass


class AIGenerationError(TheDataPacketError):
    """Raised when AI content generation fails."""

    pass


class AudioGenerationError(TheDataPacketError):
    """Raised when audio generation fails."""

    pass


class ValidationError(TheDataPacketError):
    """Raised when data validation fails."""

    pass
