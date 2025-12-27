"""Unit tests for workflows.podcast module."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from the_data_packet.sources.base import Article
from the_data_packet.workflows.podcast import PodcastPipeline, PodcastResult


class TestPodcastResult(unittest.TestCase):
    """Test cases for PodcastResult dataclass."""

    def test_podcast_result_creation_defaults(self):
        """Test PodcastResult creation with defaults."""
        result = PodcastResult()

        self.assertFalse(result.success)
        self.assertEqual(result.number_of_articles_collected, 0)
        self.assertEqual(result.articles_collected, [])
        self.assertFalse(result.script_generated)
        self.assertFalse(result.audio_generated)
        self.assertFalse(result.rss_generated)
        self.assertIsNone(result.script_path)
        self.assertIsNone(result.audio_path)
        self.assertIsNone(result.rss_path)
        self.assertIsNone(result.s3_script_url)
        self.assertIsNone(result.s3_audio_url)
        self.assertIsNone(result.s3_rss_url)
        self.assertIsNone(result.execution_time_seconds)
        self.assertIsNone(result.error_message)

    def test_podcast_result_creation_with_values(self):
        """Test PodcastResult creation with custom values."""
        result = PodcastResult(
            success=True,
            articles_collected=3,
            script_generated=True,
            audio_generated=True,
            rss_generated=True,
            script_path=Path("/tmp/script.txt"),
            audio_path=Path("/tmp/audio.mp3"),
            rss_path=Path("/tmp/feed.xml"),
            s3_script_url="https://s3.amazonaws.com/bucket/script.txt",
            s3_audio_url="https://s3.amazonaws.com/bucket/audio.mp3",
            s3_rss_url="https://s3.amazonaws.com/bucket/feed.xml",
            execution_time_seconds=45.2,
            error_message=None,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.articles_collected, 3)
        self.assertTrue(result.script_generated)
        self.assertTrue(result.audio_generated)
        self.assertTrue(result.rss_generated)
        self.assertEqual(result.script_path, Path("/tmp/script.txt"))
        self.assertEqual(result.audio_path, Path("/tmp/audio.mp3"))
        self.assertEqual(result.rss_path, Path("/tmp/feed.xml"))
        self.assertEqual(
            result.s3_script_url, "https://s3.amazonaws.com/bucket/script.txt"
        )
        self.assertEqual(
            result.s3_audio_url, "https://s3.amazonaws.com/bucket/audio.mp3"
        )
        self.assertEqual(result.s3_rss_url, "https://s3.amazonaws.com/bucket/feed.xml")
        self.assertEqual(result.execution_time_seconds, 45.2)
        self.assertIsNone(result.error_message)


class TestPodcastPipeline(unittest.TestCase):
    """Test cases for PodcastPipeline class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.show_name = "Test Podcast"
        self.mock_config.article_sources = ["wired"]
        self.mock_config.article_categories = ["security"]
        self.mock_config.max_articles_per_source = 1
        self.mock_config.output_directory = Path("/tmp/test")
        self.mock_config.generate_script = True
        self.mock_config.generate_audio = True
        self.mock_config.generate_rss = True
        self.mock_config.anthropic_api_key = "test-anthropic-key"
        self.mock_config.elevenlabs_api_key = "test-elevenlabs-key"
        self.mock_config.s3_bucket_name = "test-bucket"
        self.mock_config.aws_access_key_id = "test-access-key"

        self.sample_article = Article(
            title="Test Security Article",
            content=(
                "This is a test article about cybersecurity with sufficient content "
                "length to be valid for processing. The content needs to be longer than "
                "100 characters to pass the Article.is_valid() method validation checks "
                "which are applied in the workflow."
            ),
            author="Test Author",
            url="https://example.com/article",
            category="security",
            source="wired",
        )

    def test_sources_defined(self):
        """Test that SOURCES dictionary is properly defined."""
        self.assertIsInstance(PodcastPipeline.SOURCES, dict)
        self.assertIn("wired", PodcastPipeline.SOURCES)
        self.assertIn("techcrunch", PodcastPipeline.SOURCES)

        # Should be importable classes
        for source_class in PodcastPipeline.SOURCES.values():
            self.assertTrue(callable(source_class))

    @patch("the_data_packet.workflows.podcast.get_config")
    def test_init_with_default_config(self, mock_get_config: MagicMock):
        """Test PodcastPipeline initialization with default config."""
        mock_get_config.return_value = self.mock_config

        with patch.object(PodcastPipeline, "_validate_config"):
            pipeline = PodcastPipeline()

            self.assertEqual(pipeline.config, self.mock_config)
            self.assertIsNone(pipeline._script_generator)
            self.assertIsNone(pipeline._audio_generator)
            self.assertIsNone(pipeline._rss_generator)
            self.assertIsNone(pipeline._s3_storage)

    def test_init_with_custom_config(self):
        """Test PodcastPipeline initialization with custom config."""
        custom_config = Mock()

        with patch.object(PodcastPipeline, "_validate_config"):
            pipeline = PodcastPipeline(custom_config)

            self.assertEqual(pipeline.config, custom_config)

    @patch("the_data_packet.workflows.podcast.get_config")
    def test_validate_config_called(self, mock_get_config: MagicMock):
        """Test that _validate_config is called during initialization."""
        mock_get_config.return_value = self.mock_config

        with patch.object(PodcastPipeline, "_validate_config") as mock_validate:
            PodcastPipeline()
            mock_validate.assert_called_once()

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    @patch.object(PodcastPipeline, "_collect_articles")
    def test_run_no_articles_collected(
        self,
        mock_collect: MagicMock,
        mock_validate: MagicMock,
        mock_get_config: MagicMock,
    ):
        """Test pipeline run when no articles are collected."""
        mock_get_config.return_value = self.mock_config
        mock_collect.return_value = []

        pipeline = PodcastPipeline()
        result = pipeline.run()

        self.assertFalse(result.success)
        self.assertEqual(result.number_of_articles_collected, 0)
        self.assertEqual(result.articles_collected, [])
        self.assertIn("No new articles were collected", result.error_message)

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    @patch.object(PodcastPipeline, "_collect_articles")
    @patch.object(PodcastPipeline, "_generate_script")
    @patch.object(PodcastPipeline, "_save_script")
    def test_run_script_only_mode(
        self,
        mock_save_script: MagicMock,
        mock_generate_script: MagicMock,
        mock_collect: MagicMock,
        mock_validate: MagicMock,
        mock_get_config: MagicMock,
    ):
        """Test pipeline run in script-only mode."""
        # Configure for script-only mode
        script_only_config = Mock()
        script_only_config.show_name = "Test Podcast"
        script_only_config.article_sources = ["wired"]
        script_only_config.article_categories = ["security"]
        script_only_config.output_directory = Path("/tmp/test")
        script_only_config.generate_script = True
        script_only_config.generate_audio = False
        script_only_config.generate_rss = False
        script_only_config.anthropic_api_key = "test-key"
        script_only_config.mongodb_username = None
        script_only_config.mongodb_password = None
        script_only_config.s3_bucket_name = None  # No S3 for script-only mode
        script_only_config.aws_access_key_id = None
        script_only_config.validate_for_script_generation = Mock()

        mock_get_config.return_value = script_only_config
        mock_collect.return_value = [self.sample_article]
        mock_generate_script.return_value = "Test script content"
        mock_save_script.return_value = Path("/tmp/test/script.txt")

        pipeline = PodcastPipeline()
        result = pipeline.run()

        self.assertTrue(result.success)
        self.assertEqual(result.number_of_articles_collected, 1)
        self.assertEqual(result.articles_collected, [self.sample_article])
        self.assertTrue(result.script_generated)
        self.assertFalse(result.audio_generated)
        self.assertFalse(result.rss_generated)
        self.assertEqual(result.script_path, Path("/tmp/test/script.txt"))

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    @patch.object(PodcastPipeline, "_collect_articles")
    def test_run_exception_handling(
        self,
        mock_collect: MagicMock,
        mock_validate: MagicMock,
        mock_get_config: MagicMock,
    ):
        """Test pipeline run exception handling."""
        mock_get_config.return_value = self.mock_config
        mock_collect.side_effect = Exception("Collection failed")

        pipeline = PodcastPipeline()
        result = pipeline.run()

        self.assertFalse(result.success)
        self.assertIn("Collection failed", result.error_message)
        self.assertIsNotNone(result.execution_time_seconds)

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_collect_articles_integration(
        self, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test _collect_articles method integration."""
        mock_get_config.return_value = self.mock_config

        # Mock source classes
        mock_wired_source = Mock()
        mock_wired_source.supported_categories = ["security", "ai", "science"]
        mock_wired_source.get_latest_article.return_value = self.sample_article
        mock_wired_source.get_multiple_articles.return_value = [self.sample_article]

        with patch.dict(PodcastPipeline.SOURCES, {"wired": lambda: mock_wired_source}):
            pipeline = PodcastPipeline()
            articles = pipeline._collect_articles()

            self.assertEqual(len(articles), 1)
            # The article should be our sample article (not a mock)
            self.assertEqual(articles[0].title, self.sample_article.title)
            self.assertEqual(articles[0].content, self.sample_article.content)
            # Since max_articles_per_source is 1, it should call get_latest_article
            mock_wired_source.get_latest_article.assert_called_once_with("security")

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_collect_articles_unknown_source(
        self, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test _collect_articles with unknown source."""
        config_unknown_source = Mock()
        config_unknown_source.article_sources = ["unknown_source"]
        config_unknown_source.article_categories = ["security"]
        config_unknown_source.max_articles_per_source = 1
        mock_get_config.return_value = config_unknown_source

        pipeline = PodcastPipeline()

        articles = pipeline._collect_articles()

        # Should return empty list but not raise exception
        self.assertEqual(len(articles), 0)

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    @patch("the_data_packet.workflows.podcast.ScriptGenerator")
    def test_generate_script_lazy_loading(
        self,
        mock_script_generator_class: MagicMock,
        mock_validate: MagicMock,
        mock_get_config: MagicMock,
    ):
        """Test script generator lazy loading."""
        mock_get_config.return_value = self.mock_config
        mock_generator = Mock()
        mock_generator.generate_script.return_value = "Generated script"
        mock_script_generator_class.return_value = mock_generator

        pipeline = PodcastPipeline()
        script = pipeline._generate_script([self.sample_article])

        self.assertEqual(script, "Generated script")
        self.assertEqual(pipeline._script_generator, mock_generator)
        mock_script_generator_class.assert_called_once()

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    @patch("the_data_packet.workflows.podcast.AudioGenerator")
    def test_generate_audio_lazy_loading(
        self,
        mock_audio_generator_class: MagicMock,
        mock_validate: MagicMock,
        mock_get_config: MagicMock,
    ):
        """Test audio generator lazy loading."""
        mock_get_config.return_value = self.mock_config
        mock_generator = Mock()
        mock_audio_result = Mock()
        mock_audio_result.output_file = Path("/tmp/audio.mp3")
        mock_generator.generate_audio.return_value = mock_audio_result
        mock_audio_generator_class.return_value = mock_generator

        pipeline = PodcastPipeline()
        audio_result = pipeline._generate_audio("Test script content")

        self.assertEqual(audio_result, mock_audio_result)
        self.assertEqual(pipeline._audio_generator, mock_generator)
        mock_audio_generator_class.assert_called_once()

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    @patch("the_data_packet.core.logging.JSONLHandler.emit")  # Mock JSONL logging
    def test_save_script(
        self, mock_emit: MagicMock, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test script saving."""
        mock_get_config.return_value = self.mock_config

        pipeline = PodcastPipeline()

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch("builtins.open", create=True) as mock_open:
                with patch(
                    "the_data_packet.workflows.podcast.datetime"
                ) as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = (
                        "20231201_120000"
                    )

                    script_path = pipeline._save_script("Test script content")

                    expected_path = (
                        self.mock_config.output_directory
                        / "episode_script_20231201_120000.txt"
                    )
                    self.assertEqual(script_path, expected_path)
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                mock_open.assert_called_once_with(expected_path, "w", encoding="utf-8")

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_should_use_s3_true(
        self, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test S3 usage detection when properly configured."""
        mock_get_config.return_value = self.mock_config

        pipeline = PodcastPipeline()
        self.assertTrue(pipeline._should_use_s3())

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_should_use_s3_false(
        self, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test S3 usage detection when not configured."""
        config_no_s3 = Mock()
        config_no_s3.s3_bucket_name = None
        config_no_s3.aws_access_key_id = None
        mock_get_config.return_value = config_no_s3

        pipeline = PodcastPipeline()
        self.assertFalse(pipeline._should_use_s3())

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch("the_data_packet.workflows.podcast.MongoDBClient")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_remove_already_used_articles_with_mongodb(
        self,
        mock_validate: MagicMock,
        mock_mongodb_client: Mock,
        mock_get_config: MagicMock,
    ):
        """Test article deduplication with MongoDB integration."""
        # Setup config with MongoDB credentials
        config_with_mongo = Mock()
        config_with_mongo.mongodb_username = "test_user"
        config_with_mongo.mongodb_password = "test_password"
        mock_get_config.return_value = config_with_mongo

        # Setup MongoDB client mock
        mock_client_instance = Mock()
        mock_mongodb_client.return_value = mock_client_instance

        # Mock one article as existing, one as new
        existing_article = Article(
            title="Existing Article",
            url="https://example.com/existing",
            content="This article already exists",
            source="test",
            category="test",
        )
        new_article = Article(
            title="New Article",
            url="https://example.com/new",
            content="This is a new article",
            source="test",
            category="test",
        )

        # Mock MongoDB responses
        def mock_find_documents(collection, query):
            if query["url"] == "https://example.com/existing":
                # Article exists
                return [{"url": "https://example.com/existing"}]
            return []  # Article doesn't exist

        mock_client_instance.find_documents.side_effect = mock_find_documents

        pipeline = PodcastPipeline()
        articles = [existing_article, new_article]
        result = pipeline._remove_already_used_articles(articles)

        # Should only return new article
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "New Article")

        # Verify MongoDB client was created and called correctly
        mock_mongodb_client.assert_called_once_with(
            username="test_user", password="test_password"
        )
        self.assertEqual(mock_client_instance.find_documents.call_count, 2)

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_remove_already_used_articles_no_mongodb_credentials(
        self, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test article deduplication without MongoDB credentials."""
        # Setup config without MongoDB credentials
        config_no_mongo = Mock()
        config_no_mongo.mongodb_username = None
        config_no_mongo.mongodb_password = None
        mock_get_config.return_value = config_no_mongo

        pipeline = PodcastPipeline()
        articles = [self.sample_article]
        result = pipeline._remove_already_used_articles(articles)

        # Should return all articles when MongoDB is not configured
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.sample_article)

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch("the_data_packet.workflows.podcast.MongoDBClient")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_add_article_to_db_with_mongodb(
        self,
        mock_validate: MagicMock,
        mock_mongodb_client: Mock,
        mock_get_config: MagicMock,
    ):
        """Test adding articles to MongoDB database."""
        # Setup config with MongoDB credentials
        config_with_mongo = Mock()
        config_with_mongo.mongodb_username = "test_user"
        config_with_mongo.mongodb_password = "test_password"
        mock_get_config.return_value = config_with_mongo

        # Setup MongoDB client mock
        mock_client_instance = Mock()
        mock_mongodb_client.return_value = mock_client_instance

        pipeline = PodcastPipeline()
        articles = [self.sample_article]
        pipeline._add_article_to_db(articles)

        # Verify MongoDB client was created and insert was called
        mock_mongodb_client.assert_called_once_with(
            username="test_user", password="test_password"
        )
        mock_client_instance.insert_document.assert_called_once_with(
            "articles", self.sample_article.to_dict()
        )

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_add_article_to_db_no_mongodb_credentials(
        self, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test adding articles to database without MongoDB credentials."""
        # Setup config without MongoDB credentials
        config_no_mongo = Mock()
        config_no_mongo.mongodb_username = None
        config_no_mongo.mongodb_password = None
        mock_get_config.return_value = config_no_mongo

        pipeline = PodcastPipeline()
        articles = [self.sample_article]

        # Should not raise an error, just log warning and return
        pipeline._add_article_to_db(articles)
        # No assertions needed, just ensuring no exceptions

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch("the_data_packet.workflows.podcast.MongoDBClient")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_save_episode_metadata_with_mongodb(
        self,
        mock_validate: MagicMock,
        mock_mongodb_client: Mock,
        mock_get_config: MagicMock,
    ):
        """Test saving episode metadata to MongoDB."""
        # Setup config with MongoDB credentials
        config_with_mongo = Mock()
        config_with_mongo.mongodb_username = "test_user"
        config_with_mongo.mongodb_password = "test_password"
        mock_get_config.return_value = config_with_mongo

        # Setup MongoDB client mock
        mock_client_instance = Mock()
        mock_mongodb_client.return_value = mock_client_instance

        # Create episode result with Path objects
        episode_result = PodcastResult(
            success=True,
            articles_collected=[self.sample_article],
            script_path=Path("/tmp/script.txt"),
            audio_path=Path("/tmp/audio.wav"),
            rss_path=Path("/tmp/feed.xml"),
            execution_time_seconds=45.0,
        )

        pipeline = PodcastPipeline()
        pipeline._save_episode_metadata(episode_result)

        # Verify MongoDB client was created and insert was called
        mock_mongodb_client.assert_called_once_with(
            username="test_user", password="test_password"
        )

        # Verify insert was called once with episode metadata
        self.assertEqual(mock_client_instance.insert_document.call_count, 1)
        call_args = mock_client_instance.insert_document.call_args
        collection_name = call_args[0][0]
        episode_dict = call_args[0][1]

        self.assertEqual(collection_name, "episodes")
        self.assertTrue(episode_dict["success"])
        self.assertEqual(episode_dict["script_path"], "/tmp/script.txt")
        self.assertEqual(episode_dict["audio_path"], "/tmp/audio.wav")
        self.assertEqual(episode_dict["rss_path"], "/tmp/feed.xml")
        self.assertEqual(episode_dict["execution_time_seconds"], 45.0)

        # Verify article content was removed to save space
        article_dict = episode_dict["articles_collected"][0]
        self.assertNotIn("content", article_dict)

    @patch("the_data_packet.workflows.podcast.get_config")
    @patch.object(PodcastPipeline, "_validate_config")
    def test_save_episode_metadata_no_mongodb_credentials(
        self, mock_validate: MagicMock, mock_get_config: MagicMock
    ):
        """Test saving episode metadata without MongoDB credentials."""
        # Setup config without MongoDB credentials
        config_no_mongo = Mock()
        config_no_mongo.mongodb_username = None
        config_no_mongo.mongodb_password = None
        mock_get_config.return_value = config_no_mongo

        episode_result = PodcastResult(success=True)
        pipeline = PodcastPipeline()

        # Should not raise an error, just log warning and return
        pipeline._save_episode_metadata(episode_result)
        # No assertions needed, just ensuring no exceptions


if __name__ == "__main__":
    unittest.main()
