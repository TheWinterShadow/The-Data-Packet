"""Core exceptions for The Data Packet package."""


class TheDataPacketError(Exception):
    """Base exception for all package errors."""

    pass


class ScrapingError(TheDataPacketError):
    """Raised when there's an error during web scraping."""

    pass


class AIGenerationError(TheDataPacketError):
    """Raised when there's an error during AI content generation."""

    pass


class AudioGenerationError(TheDataPacketError):
    """Raised when there's an error during audio generation."""

    pass


class ValidationError(TheDataPacketError):
    """Raised when data validation fails."""

    pass


class NetworkError(TheDataPacketError):
    """Raised when there's a network-related error."""

    pass
