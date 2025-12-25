"""Main podcast generation workflow."""

import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from the_data_packet.core.config import Config, get_config
from the_data_packet.core.exceptions import TheDataPacketError, ValidationError
from the_data_packet.core.logging import get_logger
from the_data_packet.generation.audio import AudioGenerator, AudioResult
from the_data_packet.generation.rss import RSSGenerator
from the_data_packet.generation.script import ScriptGenerator
from the_data_packet.sources.base import Article
from the_data_packet.sources.techcrunch import TechCrunchSource
from the_data_packet.sources.wired import WiredSource
from the_data_packet.utils.mongodb import MongoDBClient
from the_data_packet.utils.s3 import S3Storage, S3UploadResult

logger = get_logger(__name__)


@dataclass
class PodcastResult:
    """Result of podcast generation workflow."""

    success: bool = False
    number_of_articles_collected: int = 0
    articles_collected: List[Article] = field(default_factory=list)
    script_generated: bool = False
    audio_generated: bool = False
    rss_generated: bool = False
    script_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    rss_path: Optional[Path] = None
    s3_script_url: Optional[str] = None
    s3_audio_url: Optional[str] = None
    s3_rss_url: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    error_message: Optional[str] = None


class PodcastPipeline:
    """Main podcast generation pipeline."""

    # Available article sources
    SOURCES = {
        "wired": WiredSource,
        "techcrunch": TechCrunchSource,
    }

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the podcast pipeline.

        Args:
            config: Pipeline configuration (defaults to global config)
        """
        self.config = config or get_config()

        # Validate configuration
        self._validate_config()

        # Initialize components (lazy loading)
        self._script_generator: Optional[ScriptGenerator] = None
        self._audio_generator: Optional[AudioGenerator] = None
        self._rss_generator: Optional[RSSGenerator] = None
        self._s3_storage: Optional[S3Storage] = None

        logger.info(f"Initialized podcast pipeline for '{self.config.show_name}'")

    def run(self) -> PodcastResult:
        """
        Execute the complete podcast generation pipeline.

        Returns:
            PodcastResult with execution details
        """
        start_time = datetime.now()
        result = PodcastResult()

        logger.info("Starting podcast generation pipeline")
        logger.info(f"Sources: {self.config.article_sources}")
        logger.info(f"Categories: {self.config.article_categories}")
        logger.info(f"Output: {self.config.output_directory}")

        try:
            # Step 1: Collect articles
            articles = self._collect_articles()
            new_articles = self._remove_already_used_articles(articles)
            result.number_of_articles_collected = len(new_articles)
            result.articles_collected = new_articles

            if not new_articles:
                raise TheDataPacketError("No new articles were collected")

            # Add used articles to database
            self._add_article_to_db(new_articles)

            # Step 2: Generate script (if enabled)
            script_content = None
            if self.config.generate_script:
                self.config.validate_for_script_generation()
                script_content = self._generate_script(articles)
                script_path = self._save_script(script_content)
                result.script_generated = True
                result.script_path = script_path

                # Upload to S3 (if configured)
                if self._should_use_s3():
                    s3_result = self._upload_to_s3(script_path)
                    result.s3_script_url = s3_result.s3_url

            # Step 3: Generate audio (if enabled)
            if self.config.generate_audio:
                if not script_content:
                    raise TheDataPacketError(
                        "Script content required for audio generation"
                    )

                self.config.validate_for_audio_generation()
                audio_result = self._generate_audio(script_content)
                result.audio_generated = True
                result.audio_path = audio_result.output_file

                # Upload to S3 (if configured)
                if self._should_use_s3():
                    s3_result = self._upload_to_s3(audio_result.output_file)
                    result.s3_audio_url = s3_result.s3_url

            # Step 4: Generate/Update RSS feed (if enabled and audio was uploaded)
            if self.config.generate_rss and result.s3_audio_url:
                self._generate_rss_feed(
                    articles,
                    result,
                    audio_result if "audio_result" in locals() else None,
                )

            # Calculate execution time
            result.execution_time_seconds = (
                datetime.now() - start_time
            ).total_seconds()
            result.success = True

            logger.info(
                f"Pipeline completed successfully in {result.execution_time_seconds:.1f} seconds"
            )

            self._save_episode_metadata(result)

            return result

        except Exception as e:
            result.execution_time_seconds = (
                datetime.now() - start_time
            ).total_seconds()
            result.error_message = str(e)

            logger.error(
                f"Pipeline failed after {result.execution_time_seconds:.1f} seconds: {e}"
            )

            return result

    def _collect_articles(self) -> List[Article]:
        """Collect articles from all configured sources."""
        logger.info("Collecting articles")

        all_articles = []

        for source_name in self.config.article_sources:
            if source_name not in self.SOURCES:
                logger.warning(f"Unknown article source: {source_name}")
                continue

            source_class = self.SOURCES[source_name]
            source = source_class()

            for category in self.config.article_categories:
                # Skip categories not supported by this source
                if category not in source.supported_categories:
                    logger.warning(
                        f"Category '{category}' not supported by {source_name}"
                    )
                    continue

                try:
                    logger.info(f"Collecting {category} articles from {source_name}")

                    if self.config.max_articles_per_source == 1:
                        article = source.get_latest_article(category)
                        all_articles.append(article)
                    else:
                        articles = source.get_multiple_articles(
                            category, self.config.max_articles_per_source
                        )
                        all_articles.extend(articles)

                except Exception as e:
                    logger.error(
                        f"Failed to collect {category} articles from {source_name}: {e}"
                    )
                    logger.error(traceback.format_exc())

        # Filter valid articles
        valid_articles = [a for a in all_articles if a.is_valid()]

        logger.info(
            f"Collected {len(valid_articles)} valid articles (out of {len(all_articles)} total)"
        )

        return valid_articles

    def _remove_already_used_articles(self, articles: List[Article]) -> List[Article]:
        """Check if the article has already been used in previous episodes.

        This prevents content duplication by checking the MongoDB 'articles' collection
        for any articles that have been used in previous podcast episodes.

        Args:
            articles: List of articles to check for duplication

        Returns:
            List of articles that have not been used before
        """
        if not self.config.mongodb_username or not self.config.mongodb_password:
            logger.warning(
                "MongoDB credentials are not configured, skipping deduplication"
            )
            return articles

        logger.info(
            f"Attempting MongoDB connection for deduplication with username: {self.config.mongodb_username}"
        )
        try:
            mongo_client = MongoDBClient(
                username=self.config.mongodb_username,
                password=self.config.mongodb_password,
            )
            logger.info("MongoDB client created successfully for deduplication")
        except Exception as e:
            logger.error(f"Failed to create MongoDB client for deduplication: {e}")
            logger.warning("Proceeding without deduplication")
            return articles

        new_articles = []

        try:
            for article in articles:
                # Check if article URL already exists in the database
                logger.debug(f"Checking if article already exists: {article.title}")
                existing = mongo_client.find_documents("articles", {"url": article.url})
                if len(list(existing)) > 0:
                    logger.info(
                        f"Article already used in previous episode: {article.title}"
                    )
                    continue
                new_articles.append(article)

            logger.info(
                f"Deduplication complete: {len(new_articles)}/{len(articles)} articles are new"
            )
        except Exception as e:
            logger.error(f"Error during deduplication: {e}")
            logger.warning("Proceeding with all articles (deduplication failed)")
            new_articles = articles
        finally:
            mongo_client.close()

        return new_articles

    def _add_article_to_db(self, articles: List[Article]) -> None:
        """Add used articles to the MongoDB database for future deduplication.

        Stores article information to prevent reuse in future episodes.
        This ensures that each podcast episode contains unique content.

        Args:
            articles: List of Article objects to store in the database
        """
        if not self.config.mongodb_username or not self.config.mongodb_password:
            logger.warning(
                "MongoDB credentials are not configured, skipping article storage"
            )
            return

        logger.info(
            f"Attempting MongoDB connection for article storage with username: {self.config.mongodb_username}"
        )
        try:
            mongo_client = MongoDBClient(
                username=self.config.mongodb_username,
                password=self.config.mongodb_password,
            )
            logger.info("MongoDB client created successfully for article storage")
        except Exception as e:
            logger.error(f"Failed to create MongoDB client for article storage: {e}")
            logger.warning("Proceeding without storing articles")
            return

        article_docs = [article.to_dict() for article in articles]
        logger.info(f"Storing {len(article_docs)} articles to MongoDB")

        try:
            for i, article in enumerate(article_docs):
                logger.debug(
                    f"Storing article {i+1}/{len(article_docs)}: {article.get('title', 'Unknown')}"
                )
                mongo_client.insert_document("articles", article)
            logger.info(
                f"Successfully stored {len(article_docs)} articles to MongoDB database"
            )
        except Exception as e:
            logger.error(f"Failed to store articles to MongoDB: {e}")
        finally:
            mongo_client.close()

    def _generate_script(self, articles: List[Article]) -> str:
        """Generate podcast script from articles."""
        logger.info("Generating podcast script")

        if not self._script_generator:
            self._script_generator = ScriptGenerator()

        return self._script_generator.generate_script(articles)

    def _generate_audio(self, script_content: str) -> AudioResult:
        """Generate audio from script."""
        logger.info("Generating podcast audio")

        if not self._audio_generator:
            self._audio_generator = AudioGenerator()

        return self._audio_generator.generate_audio(script_content)

    def _save_script(self, script_content: str) -> Path:
        """Save script to file."""
        # Ensure output directory exists
        self.config.output_directory.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp if not specified
        script_filename = (
            f"episode_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        script_path = self.config.output_directory / script_filename

        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            logger.info(f"Script saved to {script_path}")
            return script_path

        except Exception as e:
            raise TheDataPacketError(f"Failed to save script: {e}")

    def _upload_to_s3(self, file_path: Path) -> S3UploadResult:
        """Upload file to S3."""
        if not self._s3_storage:
            self._s3_storage = S3Storage()

        # Generate S3 key with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d")
        s3_key = f"{self.config.show_name.lower().replace(' ', '-')}/{timestamp}/{file_path.name}"

        return self._s3_storage.upload_file(file_path, s3_key)

    def _should_use_s3(self) -> bool:
        """Check if S3 should be used for uploads."""
        return bool(self.config.s3_bucket_name and self.config.aws_access_key_id)

    def _generate_rss_feed(
        self,
        articles: List[Article],
        result: PodcastResult,
        audio_result: Optional[AudioResult] = None,
    ) -> None:
        """Generate and upload RSS feed for the new episode."""
        try:
            logger.info("Generating RSS feed")

            if not self._rss_generator:
                self._rss_generator = RSSGenerator(self.config)

            # Determine episode number (will be auto-assigned in RSS generator)
            episode_number = None  # Let RSS generator determine the next number

            # Get audio file size if available
            file_size = None
            duration = None
            if audio_result and audio_result.output_file.exists():
                file_size = audio_result.output_file.stat().st_size
                # Duration could be extracted from audio_result if available
                duration = getattr(audio_result, "duration", None)

            # Create podcast episode from articles
            if result.s3_audio_url:
                episode = self._rss_generator.generate_episode_from_articles(
                    articles=articles,
                    audio_url=result.s3_audio_url,
                    episode_number=episode_number,
                    duration=duration,
                    file_size=file_size,
                )
            else:
                logger.error("No S3 audio URL available for RSS generation")
                return

            # Update RSS feed
            rss_result = self._rss_generator.update_rss_feed(episode)

            if rss_result.success:
                result.rss_generated = True
                result.rss_path = rss_result.local_path
                result.s3_rss_url = rss_result.s3_url
                logger.info("RSS feed updated successfully")
                if rss_result.s3_url:
                    logger.info(f"RSS feed URL: {rss_result.s3_url}")
            else:
                logger.error(f"Failed to update RSS feed: {rss_result.error_message}")

        except Exception as e:
            logger.error(f"RSS feed generation failed: {e}")
            # Don't fail the entire pipeline for RSS errors

    def _validate_config(self) -> None:
        """Validate pipeline configuration."""
        errors = []

        # Validate article sources
        unknown_sources = set(self.config.article_sources) - set(self.SOURCES.keys())
        if unknown_sources:
            errors.append(f"Unknown article sources: {', '.join(unknown_sources)}")

        # Validate that at least one generation is enabled
        if not self.config.generate_script and not self.config.generate_audio:
            errors.append(
                "At least one of generate_script or generate_audio must be enabled"
            )

        if errors:
            raise ValidationError(
                f"Configuration validation failed: {'; '.join(errors)}"
            )

    def _save_episode_metadata(self, episode_data: PodcastResult) -> None:
        """Save episode metadata to MongoDB for tracking and analytics.

        Stores comprehensive episode information including:
        - Episode success status and execution time
        - List of articles used (without full content to save space)
        - Generated file paths
        - Timestamps and other metadata

        Args:
            episode_data: PodcastResult containing episode information to save
        """
        if not self.config.mongodb_username or not self.config.mongodb_password:
            logger.warning(
                "MongoDB credentials are not configured, skipping metadata save"
            )
            return

        mongo_client = MongoDBClient(
            username=self.config.mongodb_username,
            password=self.config.mongodb_password,
        )

        # Convert the episode data to a dictionary, converting Article objects to dicts
        episode_dict = episode_data.__dict__.copy()
        episode_dict["articles_collected"] = [
            article.to_dict() for article in episode_data.articles_collected
        ]

        # Convert Path objects to strings for MongoDB compatibility
        if episode_dict.get("script_path"):
            episode_dict["script_path"] = str(episode_dict["script_path"])
        if episode_dict.get("audio_path"):
            episode_dict["audio_path"] = str(episode_dict["audio_path"])
        if episode_dict.get("rss_path"):
            episode_dict["rss_path"] = str(episode_dict["rss_path"])

        # Remove article content to save space in database
        for article in episode_dict["articles_collected"]:
            article.pop("content", None)

        mongo_client.insert_document("episodes", episode_dict)
        logger.info("Added episode metadata to MongoDB database")
