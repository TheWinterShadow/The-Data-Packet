"""Content extractor for Wired.com articles."""

import json
import logging
import re
from typing import List, Optional

from bs4 import BeautifulSoup

from the_data_packet.models import ArticleData

logger = logging.getLogger(__name__)


class WiredContentExtractor:
    """Extracts article data from Wired.com HTML pages."""

    # Text patterns to skip when extracting content
    SKIP_PATTERNS = [
        "subscribe to wired",
        "most popular",
        "related stories",
        "advertisement",
        "get wired",
        "sign up",
    ]

    def __init__(self) -> None:
        """Initialize the content extractor."""
        pass

    def extract(self, soup: BeautifulSoup, url: Optional[str] = None) -> ArticleData:
        """
        Extract article data from a BeautifulSoup object of a Wired article page.

        Args:
            soup: BeautifulSoup object of the article page
            url: Optional URL of the article

        Returns:
            ArticleData object with extracted information
        """
        logger.info("Extracting article data from Wired.com page")

        article_data = ArticleData(url=url)

        # Extract title
        article_data.title = self._extract_title(soup)

        # Extract author
        article_data.author = self._extract_author(soup)

        # Extract content
        article_data.content = self._extract_content(soup)

        logger.info(
            f"Extracted article: '{article_data.title[:50] if article_data.title else 'Unknown'}...' "
            f"by {article_data.author or 'Unknown'}"
        )

        return article_data

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the article title."""
        # Method 1: From title tag (remove site name)
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text().strip()
            # Remove " | WIRED" from the end if present
            title = re.sub(r"\s*\|\s*WIRED\s*$", "", title_text)
            if title:
                return title

        # Method 2: Try h1 tag as backup
        h1_tag = soup.find("h1")
        if h1_tag:
            title = h1_tag.get_text().strip()
            if title:
                return title

        # Method 3: Try meta property og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            content = og_title.get("content")
            if isinstance(content, str):
                return content.strip()

        logger.warning("Could not extract article title")
        return None

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the article author."""
        # Method 1: From meta tag
        author_meta = soup.find("meta", {"name": "author"})
        if author_meta and author_meta.get("content"):
            content = author_meta.get("content")
            if isinstance(content, str):
                author = content.strip()
                if author:
                    return author

        # Method 2: Try JSON-LD structured data
        json_author = self._extract_author_from_json_ld(soup)
        if json_author:
            return json_author

        # Method 3: Try byline elements
        byline_selectors = [
            ".byline",
            ".author",
            ".article-author",
            '[data-module="ArticleByline"]',
        ]

        for selector in byline_selectors:
            elements = soup.select(selector)
            for element in elements:
                author_text = element.get_text().strip()
                # Reasonable author name length
                if author_text and len(author_text) < 100:
                    return author_text

        logger.warning("Could not extract article author")
        return None

    def _extract_author_from_json_ld(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from JSON-LD structured data."""
        json_scripts = soup.find_all("script", type="application/ld+json")
        for script in json_scripts:
            try:
                script_content = script.string
                if script_content is None:
                    continue
                data = json.loads(script_content)
                if isinstance(data, list):
                    data = data[0]  # Take first item if it's a list

                # Look for author in various places
                if "author" in data:
                    author_field = data["author"]
                    if isinstance(author_field, list) and author_field:
                        author_data = author_field[0]
                        if isinstance(author_data, dict):
                            name = author_data.get("name")
                            return str(name) if name else None
                        else:
                            return str(author_data)
                    elif isinstance(author_field, dict):
                        name = author_field.get("name")
                        return str(name) if name else None
                    else:
                        return str(author_field)

            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                logger.debug(f"Error parsing JSON-LD for author: {e}")
                continue

        return None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the article content."""
        content_parts = []

        # Look for the main content container
        article_tag = soup.find("article")
        if not article_tag:
            # Try alternative selectors
            article_tag = soup.find("div", class_=re.compile(r"article|content|post"))

        if article_tag:
            # Find all paragraphs within the article
            paragraphs = article_tag.find_all("p")

            # Filter out paragraphs that are likely navigation, ads, or metadata
            for p in paragraphs:
                text = p.get_text().strip()

                # Skip very short paragraphs and common navigation text
                if len(text) < 20:
                    continue

                if self._should_skip_paragraph(text):
                    continue

                content_parts.append(text)

        if content_parts:
            content = "\n\n".join(content_parts)
            logger.info(
                f"Extracted {len(content_parts)} content paragraphs "
                f"({len(content)} characters)"
            )
            return content

        logger.warning("Could not extract article content")
        return None

    def _should_skip_paragraph(self, text: str) -> bool:
        """Check if a paragraph should be skipped based on content."""
        text_lower = text.lower()

        # Skip paragraphs containing promotional or navigation text
        for pattern in self.SKIP_PATTERNS:
            if pattern in text_lower:
                return True

        # Skip very repetitive text (likely boilerplate)
        words = text_lower.split()
        if len(set(words)) < len(words) * 0.5 and len(words) > 10:
            return True

        return False
