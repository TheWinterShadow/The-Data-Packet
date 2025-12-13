"""
Enhanced Daily News Podcast Generator
Main logic for generating podcast scripts from articles with improved error handling.
"""

from typing import Dict, List, Optional

from the_data_packet.config import get_settings
from the_data_packet.core.exceptions import AIGenerationError, ValidationError
from the_data_packet.core.logging_config import get_logger
from the_data_packet.ai.claude_client import ClaudeClient
from the_data_packet.ai.prompts import (
    ARTICLE_TO_SEGMENT_PROMPT,
    SUMMARIES_TO_FRAMEWORK_PROMPT,
    format_all_summaries,
    validate_prompt_variables,
)

logger = get_logger(__name__)


class PodcastScriptGenerator:
    """
    Enhanced generator for daily news podcast scripts from articles.

    Process:
    1. For each article → Generate segment script + summary
    2. All summaries → Generate intro, transitions, closing
    3. Combine everything into final script

    Features:
    - Better error handling and validation
    - Progress tracking
    - Configurable through settings
    - Comprehensive logging
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        show_name: Optional[str] = None,
        claude_client: Optional[ClaudeClient] = None,
    ):
        """
        Initialize the generator.

        Args:
            api_key: Anthropic API key (defaults to settings)
            show_name: Name of your podcast show (defaults to settings)
            claude_client: Pre-configured ClaudeClient instance
        """
        settings = get_settings()

        self.show_name = show_name or settings.show_name
        self.client = claude_client or ClaudeClient(api_key=api_key)

        # Storage for generated content
        self.segment_scripts: List[str] = []
        self.segment_summaries: List[str] = []
        self.framework: Optional[str] = None

        logger.info(f"Initialized PodcastScriptGenerator for show: {self.show_name}")

    def generate_segment(self, article_text: str, segment_num: int) -> Dict[str, str]:
        """
        STEP 1: Generate segment script and summary from article.

        Args:
            article_text: Full text of the article
            segment_num: Segment number (for logging)

        Returns:
            dict with 'script' and 'summary' keys

        Raises:
            AIGenerationError: If generation fails
            ValidationError: If article text is invalid
        """
        if not article_text or not article_text.strip():
            raise ValidationError("Article text cannot be empty")

        logger.info(
            f"Generating segment {segment_num} (article length: {len(article_text)} chars)"
        )

        try:
            # Validate and fill in the prompt template
            validate_prompt_variables(
                ARTICLE_TO_SEGMENT_PROMPT, article_text=article_text
            )
            prompt = ARTICLE_TO_SEGMENT_PROMPT.format(article_text=article_text)

            # Call Claude API
            full_response = self.client.chat(message=prompt, max_tokens=3000)

            if not full_response:
                raise AIGenerationError("Received empty response from Claude API")

            # Split into script and summary sections
            try:
                parts = full_response.split("### SEGMENT SUMMARY")
                if len(parts) != 2:
                    logger.warning(
                        f"Unexpected response format for segment {segment_num}"
                    )
                    # Try alternative parsing
                    parts = full_response.split("---")
                    if len(parts) < 3:
                        raise ValueError("Could not parse response sections")

                script = (
                    parts[0]
                    .replace("### SEGMENT SCRIPT", "")
                    .replace("---", "")
                    .strip()
                )
                summary = parts[1].strip() if len(parts) > 1 else ""

                if not script:
                    raise ValueError("No script content found in response")
                if not summary:
                    logger.warning(
                        f"No summary found for segment {segment_num}, creating fallback"
                    )
                    summary = self._create_fallback_summary(article_text)

            except Exception as e:
                logger.error(
                    f"Failed to parse Claude response for segment {segment_num}: {e}"
                )
                # Create fallback content
                script = full_response
                summary = self._create_fallback_summary(article_text)

            logger.info(f"Successfully generated segment {segment_num}")

            return {"script": script, "summary": summary}

        except Exception as e:
            logger.error(f"Error generating segment {segment_num}: {e}")
            raise AIGenerationError(f"Failed to generate segment {segment_num}") from e

    def _create_fallback_summary(self, article_text: str) -> str:
        """Create a basic fallback summary when parsing fails."""
        lines = article_text.strip().split("\n")
        title_line = lines[0] if lines else "Unknown Article"

        return f"""**Headline**: {title_line}
**Key Players**: See article content
**Category**: Tech News
**Tone**: Informational
**Key Takeaway**: See script for details
**Duration**: 3-4 minutes
**Opening Line**: Generated content
**Closing Line**: Generated content"""

    def generate_all_segments(self, articles: List[str]) -> List[Dict[str, str]]:
        """
        STEP 1 (repeated): Generate scripts and summaries for all articles.

        Args:
            articles: List of article texts

        Returns:
            List of dictionaries with 'script' and 'summary' keys

        Raises:
            ValidationError: If articles list is invalid
        """
        if not articles:
            raise ValidationError("Articles list cannot be empty")

        logger.info(f"Generating segments for {len(articles)} articles")

        all_segments = []

        for i, article in enumerate(articles):
            try:
                segment = self.generate_segment(article, i + 1)
                all_segments.append(segment)

                # Store for later use
                self.segment_scripts.append(segment["script"])
                self.segment_summaries.append(segment["summary"])

            except Exception as e:
                logger.error(f"Failed to generate segment {i + 1}: {e}")
                # Continue with other articles, but re-raise if this is the only article
                if len(articles) == 1:
                    raise
                continue

        if not all_segments:
            raise AIGenerationError("Failed to generate any segments")

        logger.info(f"Successfully generated {len(all_segments)} segments")
        return all_segments

    def generate_framework(self, episode_date: str) -> str:
        """
        STEP 2: Generate show opening, transitions, and closing.

        Args:
            episode_date: Date string for the episode

        Returns:
            Complete framework content

        Raises:
            AIGenerationError: If generation fails
            ValidationError: If no segments available
        """
        if not self.segment_summaries:
            raise ValidationError(
                "No segment summaries available. Generate segments first."
            )

        logger.info(
            f"Generating show framework for {len(self.segment_summaries)} segments"
        )

        try:
            # Format summaries for the prompt
            formatted_summaries = format_all_summaries(self.segment_summaries)

            # Validate and fill in the prompt template
            validate_prompt_variables(
                SUMMARIES_TO_FRAMEWORK_PROMPT,
                show_name=self.show_name,
                episode_date=episode_date,
                num_segments=len(self.segment_summaries),
                segment_summaries=formatted_summaries,
            )

            prompt = SUMMARIES_TO_FRAMEWORK_PROMPT.format(
                show_name=self.show_name,
                episode_date=episode_date,
                num_segments=len(self.segment_summaries),
                segment_summaries=formatted_summaries,
            )

            # Call Claude API
            framework_response = self.client.chat(message=prompt, max_tokens=2000)

            if not framework_response:
                raise AIGenerationError(
                    "Received empty framework response from Claude API"
                )

            self.framework = framework_response
            logger.info("Successfully generated show framework")

            return framework_response

        except Exception as e:
            logger.error(f"Error generating framework: {e}")
            raise AIGenerationError("Failed to generate show framework") from e

    def generate_complete_episode(self, articles: List[str], episode_date: str) -> str:
        """
        STEP 3: Generate complete podcast episode script.

        Args:
            articles: List of article texts
            episode_date: Date string for the episode

        Returns:
            Complete podcast script ready for TTS

        Raises:
            AIGenerationError: If generation fails
        """
        logger.info(
            f"Generating complete episode with {len(articles)} articles for {episode_date}"
        )

        try:
            # Step 1: Generate all segments
            segments = self.generate_all_segments(articles)

            # Step 2: Generate framework
            framework = self.generate_framework(episode_date)

            # Step 3: Combine everything
            complete_script = self._combine_script_parts(framework, segments)

            logger.info(
                f"Generated complete episode script ({len(complete_script)} characters)"
            )
            return complete_script

        except Exception as e:
            logger.error(f"Error generating complete episode: {e}")
            raise AIGenerationError("Failed to generate complete episode") from e

    def _combine_script_parts(
        self, framework: str, segments: List[Dict[str, str]]
    ) -> str:
        """
        Combine framework and segments into final script.

        Args:
            framework: Generated framework content
            segments: List of segment dictionaries

        Returns:
            Combined script
        """
        logger.debug("Combining script parts into final episode")

        # Parse framework sections
        framework_parts = self._parse_framework(framework)

        # Build complete script
        script_parts = []

        # Add opening
        if "opening" in framework_parts:
            script_parts.append(framework_parts["opening"])

        # Add segments with transitions
        for i, segment in enumerate(segments):
            script_parts.append(segment["script"])

            # Add transition (if not the last segment)
            if i < len(segments) - 1:
                transition_key = f"transition_{i+1}_{i+2}"
                if transition_key in framework_parts:
                    script_parts.append(framework_parts[transition_key])

        # Add closing
        if "closing" in framework_parts:
            script_parts.append(framework_parts["closing"])

        return "\n\n".join(script_parts)

    def _parse_framework(self, framework: str) -> Dict[str, str]:
        """
        Parse framework response into sections.

        Args:
            framework: Raw framework response

        Returns:
            Dictionary of framework sections
        """
        sections = {}
        current_section = None
        current_content = []

        for line in framework.split("\n"):
            line = line.strip()

            if line.startswith("## SHOW OPENING"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "opening"
                current_content = []
            elif line.startswith("## TRANSITION"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                # Extract transition number
                import re

                match = re.search(r"(\d+)→(\d+)", line)
                if match:
                    current_section = f"transition_{match.group(1)}_{match.group(2)}"
                else:
                    current_section = line.lower().replace("## ", "").replace(" ", "_")
                current_content = []
            elif line.startswith("## SHOW CLOSING"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "closing"
                current_content = []
            elif current_section and line and not line.startswith("---"):
                current_content.append(line)

        # Add the last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content)

        return sections

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about the current generation session."""
        return {
            "show_name": self.show_name,
            "segments_generated": len(self.segment_scripts),
            "has_framework": bool(self.framework),
            "total_script_length": sum(len(script) for script in self.segment_scripts),
            "framework_length": len(self.framework) if self.framework else 0,
        }
