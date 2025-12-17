"""Article source implementations for The Data Packet."""

from the_data_packet.sources.base import Article, ArticleSource
from the_data_packet.sources.techcrunch import TechCrunchSource
from the_data_packet.sources.wired import WiredSource

__all__ = [
    "ArticleSource",
    "Article",
    "TechCrunchSource",
    "WiredSource",
]
