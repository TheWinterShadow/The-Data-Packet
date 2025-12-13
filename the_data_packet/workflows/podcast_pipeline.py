"""Complete podcast generation pipeline orchestrating all components."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from the_data_packet.ai import PodcastScriptGenerator
from the_data_packet.audio import GeminiTTSGenerator
from the_data_packet.core.exceptions import TheDataPacketError, ValidationError
from the_data_packet.core.logging_config import get_logger
from the_data_packet.scrapers import WiredArticleScraper
from the_data_packet.workflows.pipeline_config import PipelineConfig

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    """Result of a complete pipeline execution."""

    success: bool
    config: PipelineConfig
    articles_scraped: int = 0
    script_generated: bool = False
    audio_generated: bool = False
    script_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    execution_time_seconds: Optional[float] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "articles_scraped": self.articles_scraped,
            "script_generated": self.script_generated,
            "audio_generated": self.audio_generated,
            "script_path": str(self.script_path) if self.script_path else None,
            "audio_path": str(self.audio_path) if self.audio_path else None,
            "execution_time_seconds": self.execution_time_seconds,
            "error_message": self.error_message,
            "config": self.config.to_dict(),
        }


class PodcastPipeline:
    """
    Complete podcast generation pipeline.

    Orchestrates:
    1. Article scraping from Wired.com
    2. AI script generation using Claude
    3. Audio generation using Gemini TTS

    Features:
    - Comprehensive error handling
    - Progress tracking
    - Configurable outputs
    - Intermediate file saving
    - Result validation
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the pipeline.

        Args:
            config: Pipeline configuration (defaults to PipelineConfig())
        """
        self.config = config or PipelineConfig()

        # Validate configuration
        validation_errors = self.config.validate()
        if validation_errors:
            raise ValidationError(
                f"Invalid configuration: {'; '.join(validation_errors)}"
            )

        # Initialize components (lazy loading)
        self._scraper: Optional[WiredArticleScraper] = None
        self._script_generator: Optional[PodcastScriptGenerator] = None
        self._audio_generator: Optional[GeminiTTSGenerator] = None

        logger.info(f"Initialized podcast pipeline for show: {self.config.show_name}")

    @property
    def scraper(self) -> WiredArticleScraper:
        """Get or create the article scraper."""
        if self._scraper is None:
            self._scraper = WiredArticleScraper()
            logger.debug("Initialized article scraper")
        return self._scraper

    @property
    def script_generator(self) -> PodcastScriptGenerator:
        """Get or create the script generator."""
        if self._script_generator is None:
            self._script_generator = PodcastScriptGenerator(
                api_key=self.config.anthropic_api_key, show_name=self.config.show_name
            )
            logger.debug("Initialized script generator")
        return self._script_generator

    @property
    def audio_generator(self) -> GeminiTTSGenerator:
        """Get or create the audio generator."""
        if self._audio_generator is None:
            self._audio_generator = GeminiTTSGenerator(
                api_key=self.config.google_api_key,
                voice_a=self.config.voice_a,
                voice_b=self.config.voice_b,
            )
            logger.debug("Initialized audio generator")
        return self._audio_generator

    def run(self) -> PipelineResult:
        """
        Execute the complete pipeline.

        Returns:
            PipelineResult with execution details
        """
        start_time = datetime.now()

        logger.info("Starting podcast generation pipeline")
        logger.info(f"Configuration: {self.config.to_dict()}")

        result = PipelineResult(success=False, config=self.config)

        try:
            # Step 1: Scrape articles
            logger.info("Step 1: Scraping articles")
            articles = self._scrape_articles()
            result.articles_scraped = len(articles)

            if not articles:
                raise TheDataPacketError("No articles were successfully scraped")

            logger.info(f"Successfully scraped {len(articles)} articles")

            # Step 2: Generate script (if enabled)
            script_content = None
            if self.config.generate_script:
                logger.info("Step 2: Generating podcast script")
                script_content = self._generate_script(articles)
                result.script_generated = True

                # Save script
                script_path = self._save_script(script_content)
                result.script_path = script_path
                logger.info(f"Script saved to: {script_path}")

            # Step 3: Generate audio (if enabled)
            if self.config.generate_audio:
                if not script_content:
                    raise TheDataPacketError(
                        "Script content required for audio generation"
                    )

                logger.info("Step 3: Generating podcast audio")
                audio_path = self._generate_audio(script_content)
                result.audio_generated = True
                result.audio_path = audio_path
                logger.info(f"Audio saved to: {audio_path}")

            # Step 4: Validation (if enabled)
            if self.config.validate_results:
                logger.info("Step 4: Validating results")
                self._validate_results(result)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time_seconds = execution_time
            result.success = True

            logger.info(
                f"Pipeline completed successfully in {execution_time:.1f} seconds"
            )

            # Cleanup (if enabled)
            if self.config.cleanup_temp_files:
                self._cleanup_temp_files()

            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time_seconds = execution_time
            result.error_message = str(e)

            logger.error(f"Pipeline failed after {execution_time:.1f} seconds: {e}")

            return result

        finally:
            self._cleanup_resources()

    def _scrape_articles(self) -> List[str]:
        """
        Scrape articles from configured categories.

        Returns:
            List of formatted article texts
        """
        all_articles = []

        for category in self.config.categories:
            logger.info(f"Scraping {category} articles")

            try:
                if self.config.max_articles_per_category == 1:
                    # Get single latest article
                    article = self.scraper.get_latest_article(category)
                    article_text = f"TITLE: {article.title}, AUTHOR: {article.author}, CONTENT: {article.content}"
                    all_articles.append(article_text)
                else:
                    # Get multiple articles
                    articles = self.scraper.get_multiple_articles(
                        category, self.config.max_articles_per_category
                    )
                    for article in articles:
                        article_text = f"TITLE: {article.title}, AUTHOR: {article.author}, CONTENT: {article.content}"
                        all_articles.append(article_text)

                logger.debug(f"Scraped {len(all_articles)} articles from {category}")

            except Exception as e:
                logger.warning(f"Failed to scrape {category} articles: {e}")
                # Continue with other categories
                continue

        return all_articles

    def _generate_script(self, articles: List[str]) -> str:
        """
        Generate podcast script from articles.

        Args:
            articles: List of article texts

        Returns:
            Complete podcast script
        """
        script = self.script_generator.generate_complete_episode(
            articles=articles, episode_date=self.config.episode_date
        )

        return script

    def _save_script(self, script_content: str) -> Path:
        """
        Save script content to file.

        Args:
            script_content: Generated script text

        Returns:
            Path to saved script file
        """
        script_path = self.config.get_script_path()

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return script_path

    def _generate_audio(self, script_content: str) -> Path:
        """
        Generate audio from script.

        Args:
            script_content: Podcast script text

        Returns:
            Path to generated audio file
        """
        audio_path = self.config.get_audio_path()

        audio_result = self.audio_generator.generate_audio(
            script=script_content, output_file=audio_path
        )

        return audio_result.output_file

    def _validate_results(self, result: PipelineResult) -> None:
        """
        Validate pipeline results.

        Args:
            result: Pipeline result to validate

        Raises:
            ValidationError: If validation fails
        """
        errors = []

        if result.script_generated and result.script_path:
            if not result.script_path.exists():
                errors.append("Script file was not created")
            elif result.script_path.stat().st_size == 0:
                errors.append("Script file is empty")

        if result.audio_generated and result.audio_path:
            if not result.audio_path.exists():
                errors.append("Audio file was not created")
            elif result.audio_path.stat().st_size == 0:
                errors.append("Audio file is empty")

        if errors:
            raise ValidationError(f"Result validation failed: {'; '.join(errors)}")

    def _cleanup_temp_files(self) -> None:
        """Clean up any temporary files created during processing."""
        # Implementation would clean up temp files
        logger.debug("Cleaning up temporary files")

    def _cleanup_resources(self) -> None:
        """Clean up resources used during pipeline execution."""
        if self._scraper:
            try:
                self._scraper.close()
            except:
                pass
        logger.debug("Cleaned up pipeline resources")

    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status and configuration."""
        return {
            "config": self.config.to_dict(),
            "components_initialized": {
                "scraper": self._scraper is not None,
                "script_generator": self._script_generator is not None,
                "audio_generator": self._audio_generator is not None,
            },
        }
