"""Script generation using Anthropic Claude."""

import re
from typing import Any, List, Optional

from anthropic import Anthropic, APIError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from the_data_packet.core.config import get_config
from the_data_packet.core.exceptions import AIGenerationError, ConfigurationError
from the_data_packet.core.logging import get_logger
from the_data_packet.sources.base import Article

logger = get_logger(__name__)


class ScriptGenerator:
    """Generates podcast scripts from articles using Claude AI."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the script generator.

        Args:
            api_key: Anthropic API key (defaults to config)
        """
        config = get_config()

        self.api_key = api_key or config.anthropic_api_key
        if not self.api_key:
            raise ConfigurationError(
                "Anthropic API key is required for script generation"
            )

        self.client = Anthropic(api_key=self.api_key)
        self.config = config

        logger.info("Initialized script generator")

    def generate_script(self, articles: List[Article]) -> str:
        """
        Generate a complete podcast script from articles.

        Args:
            articles: List of articles to convert to script

        Returns:
            Complete podcast script

        Raises:
            AIGenerationError: If script generation fails
            ValidationError: If no valid articles provided
        """
        if not articles:
            raise AIGenerationError("No articles provided for script generation")

        valid_articles = [a for a in articles if a.is_valid()]
        if not valid_articles:
            raise AIGenerationError("No valid articles provided for script generation")

        logger.info(f"Generating script from {len(valid_articles)} articles")

        try:
            # Step 1: Generate individual segments
            segments = []
            summaries = []
            processed_articles = []

            for i, article in enumerate(valid_articles, 1):
                logger.info(
                    f"Generating segment {i}/{len(valid_articles)}: {article.title}"
                )
                try:
                    segment, summary = self._generate_segment(article)
                    segments.append(segment)
                    summaries.append(summary)
                    processed_articles.append(article)
                except AIGenerationError as e:
                    if "AI refused to process content" in str(e):
                        logger.warning(f"Skipping non-tech article: {article.title}")
                        continue  # Skip this article and continue with others
                    else:
                        raise  # Re-raise other AIGenerationErrors

            if not segments:
                raise AIGenerationError("No valid tech articles were processed")

            logger.info(
                f"Successfully processed {len(processed_articles)} tech articles"
            )

            # Step 2: Generate show framework (intro, transitions, outro)
            logger.info("Generating show framework")
            framework = self._generate_framework(summaries)

            # Step 3: Combine into complete script
            complete_script = self._combine_script(framework, segments)

            # Step 4: Optimize script for ElevenLabs TTS
            optimized_script = self._optimize_script_for_tts(complete_script)

            logger.info("Script generation completed successfully")
            return optimized_script

        except Exception as e:
            if isinstance(e, AIGenerationError):
                raise
            raise AIGenerationError(f"Script generation failed: {e}")

    @retry(
        stop=stop_after_attempt(5),  # More retries for server issues
        # Faster initial retries
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type((RateLimitError, APIError)),
    )
    def _generate_segment(self, article: Article) -> tuple[str, str]:
        """Generate a segment script and summary from an article."""
        prompt = ARTICLE_TO_SEGMENT_PROMPT.format(
            article_text=f"TITLE: {article.title}\nAUTHOR: {article.author or 'Unknown'}\nCONTENT: {article.content}"
        )

        try:
            response = self.client.messages.create(
                model=self.config.claude_model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            # Get text content from response
            content_block = response.content[0]
            if hasattr(content_block, "text"):
                content = content_block.text.strip()
            else:
                raise AIGenerationError("Response content block has no text attribute")

            # Parse response to extract segment and summary
            segment, summary = self._parse_segment_response(content)

            return segment, summary

        except RateLimitError as e:
            logger.warning(f"Rate limit hit for '{article.title}': {e}")
            raise AIGenerationError(f"Rate limit exceeded: {e}")
        except APIError as e:
            logger.error(f"API error for '{article.title}': {e}")
            raise AIGenerationError(f"API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for '{article.title}': {e}")
            raise AIGenerationError(
                f"Failed to generate segment for '{article.title}': {e}"
            )

    @retry(
        stop=stop_after_attempt(5),  # More retries for server issues
        # Faster initial retries
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type((RateLimitError, APIError)),
    )
    def _generate_framework(self, summaries: List[str]) -> str:
        """Generate show opening, transitions, and closing."""
        prompt = SUMMARIES_TO_FRAMEWORK_PROMPT.format(
            show_name=self.config.show_name,
            episode_date="Today",  # TODO: Use actual episode date
            num_segments=len(summaries),
            segment_summaries=self._format_summaries(summaries),
        )

        try:
            response = self.client.messages.create(
                model=self.config.claude_model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            # Get text content from response
            content_block = response.content[0]
            if hasattr(content_block, "text"):
                return content_block.text.strip()
            else:
                raise AIGenerationError("Response content block has no text attribute")

        except Exception as e:
            raise AIGenerationError(f"Failed to generate show framework: {e}")

    def _parse_segment_response(self, response: str) -> tuple[str, str]:
        """Parse the segment response to extract script and summary."""
        # Check if AI is refusing to process the content
        if self._is_refusal_response(response):
            raise AIGenerationError(
                f"AI refused to process content: {response[:200]}..."
            )

        lines = response.split("\n")

        segment_lines = []
        summary_lines = []
        current_section = None

        for line in lines:
            line = line.strip()

            if "### SEGMENT SCRIPT" in line:
                current_section = "segment"
                continue
            elif "### SEGMENT SUMMARY" in line:
                current_section = "summary"
                continue
            elif line.startswith("---"):
                continue

            if current_section == "segment" and line:
                segment_lines.append(line)
            elif current_section == "summary" and line:
                summary_lines.append(line)

        if not segment_lines:
            raise AIGenerationError("No segment script found in response")
        if not summary_lines:
            raise AIGenerationError("No segment summary found in response")

        segment = "\n".join(segment_lines).strip()
        summary = "\n".join(summary_lines).strip()

        return segment, summary

    def _is_refusal_response(self, response: str) -> bool:
        """Check if the AI response is a refusal to process the content."""
        response_lines = response.strip().split("\n")

        # Check for the new standardized format
        if any(line.strip().startswith("NON_TECH_CONTENT:") for line in response_lines):
            return True

        # Check for legacy refusal patterns
        response_lower = response.lower()
        refusal_indicators = [
            "i appreciate you sharing this, but",
            "this article is actually",
            "not appropriate content for",
            "this isn't appropriate",
            "not a tech news story",
            "if you have an actual tech news article",
            "this doesn't contain any tech news elements",
            "this is essentially an affiliate marketing piece",
        ]
        return any(indicator in response_lower for indicator in refusal_indicators)

    def _format_summaries(self, summaries: List[str]) -> str:
        """Format summaries for the framework prompt."""
        formatted = []
        for i, summary in enumerate(summaries, 1):
            formatted.append(f"Segment {i}:\n{summary}")
        return "\n\n".join(formatted)

    def _combine_script(self, framework: str, segments: List[str]) -> str:
        """Combine framework and segments into a complete script."""
        parts = []

        # Extract framework parts
        framework_parts = self._parse_framework(framework)

        # Add opening
        if "opening" in framework_parts:
            parts.append("## SHOW OPENING")
            parts.append(framework_parts["opening"])
            parts.append("")

        # Add segments with transitions
        for i, segment in enumerate(segments):
            parts.append(f"## SEGMENT {i + 1}")
            parts.append(segment)
            parts.append("")

            # Add transition (except after last segment)
            if i < len(segments) - 1:
                transition_key = f"transition_{i+1}_{i+2}"
                if transition_key in framework_parts:
                    parts.append(f"## TRANSITION {i+1}→{i+2}")
                    parts.append(framework_parts[transition_key])
                    parts.append("")

        # Add closing
        if "closing" in framework_parts:
            parts.append("## SHOW CLOSING")
            parts.append(framework_parts["closing"])

        return "\n".join(parts)

    def _parse_framework(self, framework: str) -> dict:
        """Parse framework response into sections."""
        sections = {}
        lines = framework.split("\n")
        current_section = None
        current_lines: list[str] = []

        for line in lines:
            line = line.strip()

            if line.startswith("## SHOW OPENING"):
                if current_section and current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = "opening"
                current_lines = []
            elif line.startswith("## TRANSITION"):
                if current_section and current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                # Extract transition numbers (e.g., "1→2")
                parts = line.split()
                if len(parts) >= 2:
                    transition_id = parts[1].replace("→", "_").replace("->", "_")
                    current_section = f"transition_{transition_id}"
                current_lines = []
            elif line.startswith("## SHOW CLOSING"):
                if current_section and current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = "closing"
                current_lines = []
            elif line.startswith("---"):
                continue
            elif line:
                current_lines.append(line)

        # Add final section
        if current_section and current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

    def _optimize_script_for_tts(self, script: str) -> str:
        """Optimize script text for ElevenLabs TTS following best practices."""

        def normalize_currency(match: Any) -> str:
            """Convert currency formats for TTS."""
            currency_map = {"$": "dollars", "£": "pounds", "€": "euros", "¥": "yen"}
            currency_symbol = match.group(1)
            number = match.group(2).replace(",", "")

            if "." in number:
                dollars, cents = number.split(".")
                dollars_word = self._number_to_words(int(dollars))
                cents_word = self._number_to_words(int(cents))
                return f"{dollars_word} {currency_map.get(currency_symbol, 'currency')} and {cents_word} cents"
            else:
                number_word = self._number_to_words(int(number))
                return f"{number_word} {currency_map.get(currency_symbol, 'currency')}"

        def normalize_numbers(match: Any) -> str:
            """Convert large numbers for TTS."""
            number = int(match.group().replace(",", ""))
            return self._number_to_words(number)

        def normalize_percentages(match: Any) -> str:
            """Convert percentages for TTS."""
            number = match.group(1)
            return f"{self._number_to_words(int(number))} percent"

        def normalize_phone_numbers(match: Any) -> str:
            """Convert phone numbers for TTS."""
            parts = [match.group(1), match.group(2), match.group(3)]
            result = []
            for part in parts:
                result.append(
                    " ".join([self._number_to_words(int(digit)) for digit in part])
                )
            return ", ".join(result)

        # Apply text normalization
        text = script

        # Currency normalization
        text = re.sub(r"([$£€¥])(\d+(?:,\d{3})*(?:\.\d{2})?)", normalize_currency, text)

        # Large numbers with commas
        text = re.sub(r"\\b\\d{1,3}(?:,\\d{3})+\\b", normalize_numbers, text)

        # Percentages
        text = re.sub(r"(\\d+)%", normalize_percentages, text)

        # Phone numbers
        text = re.sub(r"(\\d{3})-(\\d{3})-(\\d{4})", normalize_phone_numbers, text)

        # URLs - simplify for speech
        text = re.sub(r"https?://([\w.-]+)", r"\1", text)

        # Abbreviations expansion
        abbreviations = {
            "AI": "artificial intelligence",
            "ML": "machine learning",
            "CEO": "C.E.O.",
            "CTO": "C.T.O.",
            "CFO": "C.F.O.",
            "IPO": "I.P.O.",
            "API": "A.P.I.",
            "GPU": "G.P.U.",
            "CPU": "C.P.U.",
            "IoT": "Internet of Things",
            "VR": "virtual reality",
            "AR": "augmented reality",
            "SaaS": "Software as a Service",
            "AWS": "Amazon Web Services",
            "SDK": "software development kit",
            "vs.": "versus",
            "etc.": "etcetera",
            "Dr.": "Doctor",
            "Mr.": "Mister",
            "Ms.": "Miss",
            "Inc.": "Incorporated",
            "Corp.": "Corporation",
            "Ltd.": "Limited",
        }

        for abbrev, expansion in abbreviations.items():
            # Use word boundaries to avoid partial matches
            text = re.sub(rf"\b{re.escape(abbrev)}\b", expansion, text)

        # Add natural pauses for better flow
        # After introductory phrases
        text = re.sub(
            r"(Speaking of|Now,|Meanwhile,|However,|Actually,)",
            r'\1 <break time="0.3s"/>',
            text,
        )

        # Before important statements
        text = re.sub(
            r"(But here\'s the thing|The key point is|What\'s interesting is)",
            r'<break time="0.5s"/> \1',
            text,
        )

        # Improve punctuation for speech flow
        # Convert ellipses to pauses
        text = re.sub(r"\.\.\. ?", ' <break time="0.7s"/> ', text)

        # Add slight pauses after em dashes
        text = re.sub(r" — ", ' <break time="0.2s"/> ', text)

        return text

    def _number_to_words(self, number: int) -> str:
        """Convert numbers to words for better TTS pronunciation."""
        if number == 0:
            return "zero"

        # Handle basic numbers (this is a simplified version)
        ones = [
            "",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
        ]
        teens = [
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        ]
        tens = [
            "",
            "",
            "twenty",
            "thirty",
            "forty",
            "fifty",
            "sixty",
            "seventy",
            "eighty",
            "ninety",
        ]

        if number < 10:
            return ones[number]
        elif number < 20:
            return teens[number - 10]
        elif number < 100:
            return tens[number // 10] + (
                "" if number % 10 == 0 else " " + ones[number % 10]
            )
        elif number < 1000:
            return (
                ones[number // 100]
                + " hundred"
                + (
                    ""
                    if number % 100 == 0
                    else " " + self._number_to_words(number % 100)
                )
            )
        elif number < 1000000:
            return (
                self._number_to_words(number // 1000)
                + " thousand"
                + (
                    ""
                    if number % 1000 == 0
                    else " " + self._number_to_words(number % 1000)
                )
            )
        elif number < 1000000000:
            return (
                self._number_to_words(number // 1000000)
                + " million"
                + (
                    ""
                    if number % 1000000 == 0
                    else " " + self._number_to_words(number % 1000000)
                )
            )
        else:
            return str(number)  # Fallback for very large numbers


# Prompts (simplified versions of the original prompts)
ARTICLE_TO_SEGMENT_PROMPT = """You are writing ONE story segment for a daily tech news podcast. Convert the provided article into a focused news discussion segment between two hosts (Alex and Sam).

IMPORTANT: If the article is NOT about technology (e.g., lifestyle, shopping, health, sports, etc.), respond with: "NON_TECH_CONTENT: This article is not appropriate for a tech news podcast as it covers [category] rather than technology."

## REQUIREMENTS
- 3-4 minutes of dialogue (450-650 words)
- Conversational style with natural reactions
- Alex is relatable, Sam is tech-savvy
- Start in media res, end with clear takeaway
- Include core news, key players, impact, and next steps

## WRITING FOR AUDIO
- Use full words instead of abbreviations when possible (write "artificial intelligence" instead of "AI" when it flows better)
- Write out numbers naturally ("fifty million" instead of "50M")
- Use natural speech patterns with contractions ("don't", "we're", "it's")
- Add natural conversation fillers occasionally ("you know", "I mean", "actually")
- Use punctuation that helps with speech flow (commas for pauses, periods for stops)

## OUTPUT FORMAT
### SEGMENT SCRIPT
Alex: [dialogue]
Sam: [dialogue]
[Continue with full dialogue...]

### SEGMENT SUMMARY
**Headline**: [One-line summary]
**Key Players**: [Who's involved]
**Category**: [Type of news]
**Key Takeaway**: [Main point]

## ARTICLE TO CONVERT
{article_text}"""

SUMMARIES_TO_FRAMEWORK_PROMPT = """You are producing the framing elements of a daily news podcast episode. Create show opening, transitions between segments, and show closing.

## SHOW INFO
**Show Name**: {show_name}
**Episode Date**: {episode_date}
**Number of Stories**: {num_segments}

## OUTPUT FORMAT
## SHOW OPENING
Alex: [Energetic intro previewing all stories - 60-90 seconds]
Sam: [Natural response and story preview]
[Continue with full dialogue in this format...]

## TRANSITION 1→2
[Brief bridge - 15-30 seconds]

## SHOW CLOSING
Alex: [Wrap-up and sign-off - 45-60 seconds]
Sam: [Natural response and final sign-off]
[Continue with full dialogue in this format...]

## IMPORTANT
- Use the EXACT same dialogue format as segments: "Alex: [text]" and "Sam: [text]"
- NO bold formatting (**Alex:**) in opening or closing
- NO special formatting like \n - use natural line breaks
- Keep the conversational, natural tone consistent with segments

## SEGMENT SUMMARIES
{segment_summaries}"""
