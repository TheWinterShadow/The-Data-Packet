"""
The Data Packet - A comprehensive Python package for automated podcast generation from news articles.

This package provides end-to-end tools for:
- Scraping articles from Wired.com
- Generating podcast scripts using Claude AI
- Creating audio content using Gemini TTS
- Complete workflow orchestration

Main Components:
- PodcastPipeline: Complete workflow orchestration
- WiredArticleScraper: Article scraping and extraction
- PodcastScriptGenerator: AI-powered script generation
- GeminiTTSGenerator: Multi-speaker audio generation
- Settings: Configuration management

Quick Start:
    >>> from the_data_packet import PodcastPipeline, PipelineConfig
    >>> config = PipelineConfig()
    >>> pipeline = PodcastPipeline(config)
    >>> result = pipeline.run()

Individual Components:
    >>> from the_data_packet import WiredArticleScraper, PodcastScriptGenerator, GeminiTTSGenerator
    >>> scraper = WiredArticleScraper()
    >>> script_gen = PodcastScriptGenerator(api_key="your-key")
    >>> audio_gen = GeminiTTSGenerator(api_key="your-key")
"""

# Initialize package-level logging
import logging

from the_data_packet.__about__ import __version__
from the_data_packet.ai import ClaudeClient, PodcastScriptGenerator
from the_data_packet.audio import GeminiTTSGenerator
from the_data_packet.clients import HTTPClient, RSSClient

# Core configuration and logging
from the_data_packet.config import Settings, get_settings
from the_data_packet.core import get_logger, setup_logging
from the_data_packet.extractors import WiredContentExtractor

# Data models and utilities
from the_data_packet.models import ArticleData

# Individual components
from the_data_packet.scrapers import WiredArticleScraper

# Main workflow
from the_data_packet.workflows import PipelineConfig, PodcastPipeline

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Define what gets imported with "from the_data_packet import *"
__all__ = [
    # Version
    "__version__",
    # Configuration
    "Settings",
    "get_settings",
    "setup_logging",
    "get_logger",
    # Main workflow
    "PodcastPipeline",
    "PipelineConfig",
    # Core components
    "WiredArticleScraper",
    "PodcastScriptGenerator",
    "GeminiTTSGenerator",
    "ClaudeClient",
    # Data models
    "ArticleData",
    # Utilities
    "HTTPClient",
    "RSSClient",
    "WiredContentExtractor",
]
