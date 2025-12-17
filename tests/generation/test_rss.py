"""Unit tests for generation.rss module."""

import unittest
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from the_data_packet.generation.rss import (
    PodcastEpisode,
    RSSGenerationResult,
    RSSGenerator,
)
from the_data_packet.sources.base import Article


class TestPodcastEpisode(unittest.TestCase):
    """Test cases for PodcastEpisode dataclass."""

    def test_podcast_episode_creation(self):
        """Test PodcastEpisode creation with required fields."""
        pub_date = datetime(2023, 10, 15, 10, 30)
        episode = PodcastEpisode(
            title="Test Episode",
            description="Test Description",
            audio_url="https://example.com/audio.mp3",
            pub_date=pub_date,
        )

        self.assertEqual(episode.title, "Test Episode")
        self.assertEqual(episode.description, "Test Description")
        self.assertEqual(episode.audio_url, "https://example.com/audio.mp3")
        self.assertEqual(episode.pub_date, pub_date)
        self.assertIsNone(episode.episode_number)
        self.assertIsNone(episode.duration)
        self.assertIsNone(episode.file_size)
        self.assertIsNotNone(episode.guid)  # Should be auto-generated

    def test_podcast_episode_with_all_fields(self):
        """Test PodcastEpisode creation with all fields."""
        pub_date = datetime(2023, 10, 15, 10, 30)
        episode = PodcastEpisode(
            title="Complete Episode",
            description="Complete Description",
            audio_url="https://example.com/audio.mp3",
            pub_date=pub_date,
            episode_number=42,
            duration="01:23:45",
            file_size=1024000,
            guid="custom-guid-123",
            author="Test Author",
        )

        self.assertEqual(episode.episode_number, 42)
        self.assertEqual(episode.duration, "01:23:45")
        self.assertEqual(episode.file_size, 1024000)
        self.assertEqual(episode.guid, "custom-guid-123")
        self.assertEqual(episode.author, "Test Author")

    def test_guid_auto_generation(self):
        """Test that GUID is auto-generated when not provided."""
        pub_date = datetime(2023, 10, 15, 10, 30)
        episode = PodcastEpisode(
            title="Test Episode Title",
            description="Test Description",
            audio_url="https://example.com/audio.mp3",
            pub_date=pub_date,
        )

        # Should generate GUID based on date and title
        expected_guid = "20231015-test-episode-title"
        self.assertEqual(episode.guid, expected_guid)

    def test_guid_not_overridden_when_provided(self):
        """Test that provided GUID is not overridden."""
        pub_date = datetime(2023, 10, 15, 10, 30)
        episode = PodcastEpisode(
            title="Test Episode",
            description="Test Description",
            audio_url="https://example.com/audio.mp3",
            pub_date=pub_date,
            guid="custom-guid",
        )

        self.assertEqual(episode.guid, "custom-guid")


class TestRSSGenerationResult(unittest.TestCase):
    """Test cases for RSSGenerationResult dataclass."""

    def test_rss_generation_result_defaults(self):
        """Test RSSGenerationResult default values."""
        result = RSSGenerationResult()

        self.assertFalse(result.success)
        self.assertIsNone(result.rss_content)
        self.assertIsNone(result.local_path)
        self.assertIsNone(result.s3_url)
        self.assertIsNone(result.error_message)

    def test_rss_generation_result_with_values(self):
        """Test RSSGenerationResult with custom values."""
        result = RSSGenerationResult(
            success=True,
            rss_content="<rss>content</rss>",
            local_path=Path("/tmp/feed.xml"),
            s3_url="https://s3.example.com/feed.xml",
            error_message="Test error",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.rss_content, "<rss>content</rss>")
        self.assertEqual(result.local_path, Path("/tmp/feed.xml"))
        self.assertEqual(result.s3_url, "https://s3.example.com/feed.xml")
        self.assertEqual(result.error_message, "Test error")


class TestRSSGenerator(unittest.TestCase):
    """Test cases for RSSGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.show_name = "Test Podcast"
        self.mock_config.rss_channel_title = "Test Podcast"
        self.mock_config.rss_channel_description = "Test Description"
        self.mock_config.rss_channel_link = "https://example.com"
        self.mock_config.rss_channel_image_url = "https://example.com/image.jpg"
        self.mock_config.rss_channel_email = "test@example.com"
        self.mock_config.output_directory = Path("/tmp/test")
        self.mock_config.s3_bucket_name = "test-bucket"
        self.mock_config.aws_access_key_id = "test-access-key"

    def test_init_with_default_config(self):
        """Test RSSGenerator initialization with default config."""
        with patch("the_data_packet.generation.rss.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config
            generator = RSSGenerator()
            self.assertEqual(generator.config, self.mock_config)

    def test_init_with_custom_config(self):
        """Test RSSGenerator initialization with custom config."""
        custom_config = Mock()
        generator = RSSGenerator(custom_config)
        self.assertEqual(generator.config, custom_config)

    def test_get_next_episode_number_empty_list(self):
        """Test episode number generation with empty list."""
        generator = RSSGenerator(self.mock_config)
        episode_number = generator._get_next_episode_number([])
        self.assertEqual(episode_number, 1)

    def test_get_next_episode_number_with_existing_episodes(self):
        """Test episode number generation with existing episodes."""
        generator = RSSGenerator(self.mock_config)

        existing_episodes = [
            Mock(episode_number=1),
            Mock(episode_number=3),
            Mock(episode_number=2),
        ]

        episode_number = generator._get_next_episode_number(existing_episodes)
        self.assertEqual(episode_number, 4)

    def test_get_next_episode_number_with_none_values(self):
        """Test episode number generation with None episode numbers."""
        generator = RSSGenerator(self.mock_config)

        existing_episodes = [
            Mock(episode_number=None),
            Mock(episode_number=5),
            Mock(episode_number=None),
        ]

        episode_number = generator._get_next_episode_number(existing_episodes)
        self.assertEqual(episode_number, 6)

    def test_generate_episode_from_articles(self):
        """Test episode generation from articles."""
        generator = RSSGenerator(self.mock_config)

        articles = [
            Article(
                title="Test Article 1",
                content="Test content 1",
                url="https://example.com/1",
                author="Author 1",
            ),
            Article(
                title="Test Article 2",
                content="Test content 2",
                url="https://example.com/2",
                author="Author 2",
            ),
        ]

        audio_url = "https://example.com/audio.mp3"

        episode = generator.generate_episode_from_articles(
            articles=articles,
            audio_url=audio_url,
            episode_number=42,
            duration="01:30:00",
            file_size=2048000,
        )

        self.assertEqual(episode.episode_number, 42)
        self.assertEqual(episode.audio_url, audio_url)
        self.assertEqual(episode.duration, "01:30:00")
        self.assertEqual(episode.file_size, 2048000)
        self.assertIn("Test Article 1", episode.description)
        self.assertIn("Test Article 2", episode.description)
        self.assertIn("https://example.com/1", episode.description)

    def test_generate_rss_feed_basic(self):
        """Test RSS feed generation with basic episode."""
        generator = RSSGenerator(self.mock_config)

        episodes = [
            PodcastEpisode(
                title="Episode 1",
                description="First episode",
                audio_url="https://example.com/ep1.mp3",
                pub_date=datetime(2023, 10, 15, 10, 30),
                episode_number=1,
            )
        ]

        rss_content = generator.generate_rss_feed(episodes)

        # Parse the XML to verify structure
        root = ET.fromstring(rss_content)

        # Check root element
        self.assertEqual(root.tag, "rss")
        self.assertEqual(root.get("version"), "2.0")

        # Check channel exists
        channel = root.find("channel")
        self.assertIsNotNone(channel)

        # Check channel metadata
        title_elem = channel.find("title")
        self.assertIsNotNone(title_elem)
        self.assertEqual(title_elem.text, "Test Podcast")

        # Check episode item
        items = channel.findall("item")
        self.assertEqual(len(items), 1)

        item = items[0]
        item_title = item.find("title")
        self.assertEqual(item_title.text, "Episode 1")

    def test_get_ordinal_suffix(self):
        """Test ordinal suffix generation."""
        generator = RSSGenerator(self.mock_config)

        test_cases = [
            (1, "st"),
            (2, "nd"),
            (3, "rd"),
            (4, "th"),
            (5, "th"),
            (11, "th"),
            (12, "th"),
            (13, "th"),
            (14, "th"),
            (21, "st"),
            (22, "nd"),
            (23, "rd"),
            (24, "th"),
            (31, "st"),
        ]

        for day, expected_suffix in test_cases:
            with self.subTest(day=day):
                suffix = generator._get_ordinal_suffix(day)
                self.assertEqual(suffix, expected_suffix)

    def test_load_existing_feed_valid_xml(self):
        """Test loading existing RSS feed from valid XML."""
        generator = RSSGenerator(self.mock_config)

        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
            <channel>
                <title>Test Podcast</title>
                <item>
                    <title>Episode 1</title>
                    <description>First episode description</description>
                    <enclosure url="https://example.com/ep1.mp3" type="audio/mpeg" length="1024000"/>
                    <guid>episode-1-guid</guid>
                    <pubDate>Sun, 15 Oct 2023 10:30:00 +0000</pubDate>
                    <itunes:duration>30:00</itunes:duration>
                    <itunes:episode>1</itunes:episode>
                    <itunes:author>Test Author</itunes:author>
                </item>
            </channel>
        </rss>"""

        episodes = generator.load_existing_feed(rss_xml)

        self.assertEqual(len(episodes), 1)
        episode = episodes[0]
        self.assertEqual(episode.title, "Episode 1")
        self.assertEqual(episode.description, "First episode description")
        self.assertEqual(episode.audio_url, "https://example.com/ep1.mp3")
        self.assertEqual(episode.episode_number, 1)
        self.assertEqual(episode.duration, "30:00")
        self.assertEqual(episode.file_size, 1024000)

    def test_load_existing_feed_invalid_xml(self):
        """Test loading existing RSS feed from invalid XML."""
        generator = RSSGenerator(self.mock_config)

        invalid_xml = "This is not valid XML"
        episodes = generator.load_existing_feed(invalid_xml)

        self.assertEqual(episodes, [])

    def test_should_use_s3_true(self):
        """Test S3 usage detection when configured."""
        generator = RSSGenerator(self.mock_config)
        self.assertTrue(generator._should_use_s3())

    def test_should_use_s3_false_no_bucket(self):
        """Test S3 usage detection without bucket name."""
        config = Mock()
        config.s3_bucket_name = None
        config.aws_access_key_id = "test-access-key"

        generator = RSSGenerator(config)
        self.assertFalse(generator._should_use_s3())

    def test_should_use_s3_false_no_access_key(self):
        """Test S3 usage detection without access key."""
        config = Mock()
        config.s3_bucket_name = "test-bucket"
        config.aws_access_key_id = None

        generator = RSSGenerator(config)
        self.assertFalse(generator._should_use_s3())

    def test_format_rfc822_date(self):
        """Test RFC 822 date formatting."""
        generator = RSSGenerator(self.mock_config)

        test_datetime = datetime(2023, 10, 15, 14, 30, 45)
        formatted_date = generator._format_rfc822_date(test_datetime)

        self.assertEqual(formatted_date, "Sun, 15 Oct 2023 14:30:45 +0000")


if __name__ == "__main__":
    unittest.main()
