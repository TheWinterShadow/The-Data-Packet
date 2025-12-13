"""
Daily News Podcast Generator
Main logic for generating podcast scripts from articles.
Updated with TTS-optimized output format for Gemini 2.5
"""

import os
from datetime import datetime
from typing import Dict, List

from the_data_packet.genai.prompts import (
    ARTICLE_TO_SEGMENT_PROMPT,
    SUMMARIES_TO_FRAMEWORK_PROMPT,
    format_all_summaries,
)
from the_data_packet.utils.claude_client import ClaudeClient


class PodcastScriptGenerator:
    """
    Generates daily news podcast scripts from articles.

    Process:
    1. For each article → Generate segment script + summary
    2. All summaries → Generate intro, transitions, closing
    3. Combine everything into final script
    """

    def __init__(self, api_key: str = None, show_name: str = "Tech Daily"):
        """
        Initialize the generator.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            show_name: Name of your podcast show
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set ANTHROPIC_API_KEY or pass api_key parameter.")

        self.client = ClaudeClient(api_key=self.api_key)
        self.show_name = show_name

        # Storage for generated content
        self.segment_scripts = []
        self.segment_summaries = []
        self.framework = None

    def generate_segment(self, article_text: str, segment_num: int) -> Dict[str, str]:
        """
        STEP 1: Generate segment script and summary from article.

        Args:
            article_text: Full text of the article
            segment_num: Segment number (for logging)

        Returns:
            dict with 'script' and 'summary' keys
        """
        print(f"📰 Generating segment {segment_num}...")

        # Fill in the prompt template
        prompt: str = ARTICLE_TO_SEGMENT_PROMPT.format(
            article_text=article_text)

        # Call Claude API
        full_response = self.client.chat(
            max_tokens=3000,
            message=prompt
        )

        # Split into script and summary sections
        try:
            parts = full_response.split("### SEGMENT SUMMARY")
            script = parts[0].replace("### SEGMENT SCRIPT", "").strip()
            summary = parts[1].strip() if len(parts) > 1 else ""

            if not script or not summary:
                raise ValueError(
                    "Failed to parse script or summary from response")

        except Exception as e:
            print(f"⚠️  Warning: Could not parse response properly: {e}")
            # Fallback: use entire response as script
            script = full_response
            summary = "**Headline**: Segment content\n**Key Takeaway**: See script for details"

        print(f"✅ Segment {segment_num} complete\n")

        return {
            "script": script,
            "summary": summary
        }

    def generate_all_segments(self, articles: List[str]) -> List[Dict[str, str]]:
        """
        STEP 1 (repeated): Generate scripts and summaries for all articles.

        Args:
            articles: List of article texts

        Returns:
            List of dicts with 'script' and 'summary' for each article
        """
        results = []

        for i, article in enumerate(articles, start=1):
            result = self.generate_segment(article, segment_num=i)
            results.append(result)

            # Store for later use
            self.segment_scripts.append(result["script"])
            self.segment_summaries.append(result["summary"])

        return results

    def generate_framework(self, episode_date: str = None) -> Dict[str, str]:
        """
        STEP 2: Generate intro, transitions, and closing from summaries.

        Args:
            episode_date: Date string for episode (defaults to today)

        Returns:
            dict with 'opening', 'transitions', 'closing' keys
        """
        if not self.segment_summaries:
            raise ValueError(
                "No segment summaries available. Run generate_all_segments first.")

        print("🎙️  Generating show framework (intro, transitions, closing)...")

        # Prepare the episode date
        if episode_date is None:
            episode_date = datetime.now().strftime("%A, %B %d, %Y")

        # Format all summaries for the prompt
        summaries_text = format_all_summaries(self.segment_summaries)

        # Fill in the prompt template
        prompt = SUMMARIES_TO_FRAMEWORK_PROMPT.format(
            show_name=self.show_name,
            episode_date=episode_date,
            num_segments=len(self.segment_summaries),
            segment_summaries=summaries_text
        )

        # Call Claude API
        full_response = self.client.chat(
            max_tokens=4000,
            message=prompt
        )

        # Parse the response into sections
        framework = self._parse_framework(full_response)
        self.framework = framework

        print("✅ Framework complete\n")

        return framework

    def _parse_framework(self, response: str) -> Dict[str, str]:
        """
        Parse the framework response into opening, transitions, and closing.

        Args:
            response: Full response from Claude

        Returns:
            dict with parsed sections
        """
        sections = {
            "opening": "",
            "transitions": [],
            "closing": ""
        }

        # Split by section markers
        parts = response.split("---")

        for part in parts:
            part = part.strip()

            if "SHOW OPENING" in part:
                sections["opening"] = part.replace(
                    "## SHOW OPENING", "").strip()

            elif "TRANSITION" in part:
                sections["transitions"].append(part)

            elif "SHOW CLOSING" in part:
                sections["closing"] = part.replace(
                    "## SHOW CLOSING", "").strip()

        return sections

    def assemble_final_script(self, output_format: str = "tts") -> str:
        """
        STEP 3: Combine everything into final podcast script.

        Args:
            output_format: Format type
                - "tts": Clean dialogue-only format for Gemini 2.5 TTS
                - "readable": Human-readable format with section headers
                - "both": Returns dict with both formats

        Returns:
            Complete podcast script as string (or dict if output_format="both")
        """
        if not self.segment_scripts or not self.framework:
            raise ValueError(
                "Missing segments or framework. Generate them first.")

        print("🔧 Assembling final script...")

        if output_format == "tts":
            final_script = self._assemble_tts_format()
        elif output_format == "readable":
            final_script = self._assemble_readable_format()
        elif output_format == "both":
            final_script = {
                "tts": self._assemble_tts_format(),
                "readable": self._assemble_readable_format()
            }
        else:
            raise ValueError(
                f"Invalid output_format: {output_format}. Use 'tts', 'readable', or 'both'")

        print("✅ Final script assembled\n")

        return final_script

    def _assemble_tts_format(self) -> str:
        """
        Assemble script in TTS-optimized format for Gemini 2.5.

        Format optimized for Gemini 2.5 native TTS:
        - Clean dialogue only (no headers, dividers, or metadata)
        - Speaker labels: "Alex:" and "Sam:"
        - Natural line breaks between speakers
        - No stage directions, timestamps, or formatting
        - Double line breaks between major sections for natural pacing

        Returns:
            TTS-ready script with just dialogue
        """
        dialogue_parts = []

        # Extract just the dialogue from opening
        opening_dialogue = self._extract_dialogue(self.framework["opening"])
        if opening_dialogue:
            dialogue_parts.append(opening_dialogue)

        # Add each segment with transitions
        for i, segment_script in enumerate(self.segment_scripts):
            segment_dialogue = self._extract_dialogue(segment_script)
            if segment_dialogue:
                dialogue_parts.append(segment_dialogue)

            # Add transition dialogue (if not last segment)
            if i < len(self.segment_scripts) - 1:
                if i < len(self.framework["transitions"]):
                    transition_dialogue = self._extract_dialogue(
                        self.framework["transitions"][i])
                    if transition_dialogue:
                        dialogue_parts.append(transition_dialogue)

        # Add closing dialogue
        closing_dialogue = self._extract_dialogue(self.framework["closing"])
        if closing_dialogue:
            dialogue_parts.append(closing_dialogue)

        # Join all parts with double line break for natural pacing
        return "\n\n".join(dialogue_parts)

    def _assemble_readable_format(self) -> str:
        """
        Assemble script in human-readable format with clear sections.

        Returns:
            Formatted script with headers and sections
        """
        script_parts = []

        # 1. Add opening
        script_parts.append("=" * 80)
        script_parts.append("PODCAST EPISODE SCRIPT")
        script_parts.append("=" * 80)
        script_parts.append("")
        script_parts.append(self.framework["opening"])
        script_parts.append("")

        # 2. Add each segment with transitions
        for i, segment_script in enumerate(self.segment_scripts):
            # Add segment
            script_parts.append("-" * 80)
            script_parts.append(f"SEGMENT {i + 1}")
            script_parts.append("-" * 80)
            script_parts.append("")
            script_parts.append(segment_script)
            script_parts.append("")

            # Add transition (if not last segment)
            if i < len(self.segment_scripts) - 1:
                if i < len(self.framework["transitions"]):
                    script_parts.append("-" * 80)
                    script_parts.append(f"TRANSITION {i + 1} → {i + 2}")
                    script_parts.append("-" * 80)
                    script_parts.append("")
                    script_parts.append(self.framework["transitions"][i])
                    script_parts.append("")

        # 3. Add closing
        script_parts.append("-" * 80)
        script_parts.append("CLOSING")
        script_parts.append("-" * 80)
        script_parts.append("")
        script_parts.append(self.framework["closing"])
        script_parts.append("")
        script_parts.append("=" * 80)
        script_parts.append("END OF EPISODE")
        script_parts.append("=" * 80)

        return "\n".join(script_parts)

    def _extract_dialogue(self, text: str) -> str:
        """
        Extract just the dialogue from text, removing headers and metadata.

        This creates clean dialogue-only text suitable for TTS systems like Gemini 2.5.

        Args:
            text: Text that may contain headers, dividers, and dialogue

        Returns:
            Clean dialogue with only speaker labels and speech
        """
        lines = text.split('\n')
        dialogue_lines = []

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip headers and formatting
            if line.startswith('#'):
                continue
            if line.startswith('---'):
                continue
            if line.startswith('==='):
                continue
            if line.startswith('*'):
                continue
            if line.startswith('SEGMENT'):
                continue
            if line.startswith('TRANSITION'):
                continue
            if line.startswith('SHOW'):
                continue
            if line.startswith('CLOSING'):
                continue
            if line.startswith('['):  # Skip stage directions
                continue

            # Keep lines that look like dialogue (start with speaker name)
            if line.startswith('Alex:') or line.startswith('Sam:'):
                dialogue_lines.append(line)

        return '\n'.join(dialogue_lines)

    def generate_complete_episode(
        self,
        articles: List[str],
        episode_date: str = None,
        output_format: str = "tts"
    ) -> str:
        """
        Complete workflow: articles → final podcast script.

        This is the main method you'll use. It runs all 3 steps:
        1. Generate segment scripts + summaries for each article
        2. Generate intro, transitions, closing from summaries
        3. Combine everything into final script

        Args:
            articles: List of article texts
            episode_date: Optional date string (defaults to today)
            output_format: Format type - "tts", "readable", or "both"

        Returns:
            Complete podcast script (or dict if output_format="both")
        """
        print("=" * 80)
        print(f"🎬 GENERATING PODCAST EPISODE: {self.show_name}")
        print(
            f"📅 Date: {episode_date or datetime.now().strftime('%A, %B %d, %Y')}")
        print(f"📰 Stories: {len(articles)}")
        print(f"📤 Output Format: {output_format}")
        print("=" * 80)
        print("")

        # Step 1: Generate all segments
        print("STEP 1: Generating segment scripts and summaries...")
        print("-" * 80)
        self.generate_all_segments(articles)

        # Step 2: Generate framework
        print("STEP 2: Generating show framework...")
        print("-" * 80)
        self.generate_framework(episode_date)

        # Step 3: Assemble final script
        print("STEP 3: Assembling final script...")
        print("-" * 80)
        final_script = self.assemble_final_script(output_format=output_format)

        # Summary
        estimated_duration = len(self.segment_scripts) * \
            3.5 + 2.5  # segments + intro/outro

        print("=" * 80)
        print("🎉 EPISODE COMPLETE!")
        print(f"📊 Segments: {len(self.segment_scripts)}")
        print(f"⏱️  Estimated duration: ~{estimated_duration:.0f} minutes")
        if output_format == "both":
            print(f"📄 TTS script length: {len(final_script['tts'])} chars")
            print(
                f"📄 Readable script length: {len(final_script['readable'])} chars")
        else:
            print(f"📄 Script length: {len(final_script)} chars")
        print("=" * 80)
        print("")

        return final_script

    def save_script(self, script: str | Dict, filename: str = None, output_format: str = None) -> str | Dict:
        """
        Save script to file(s).

        Args:
            script: The script text to save (or dict with 'tts' and 'readable' keys)
            filename: Optional filename (defaults to dated filename)
            output_format: Optional format override if script is a string

        Returns:
            Path to saved file (or dict of paths if script is dict)
        """
        if filename is None:
            date_str = datetime.now().strftime("%Y%m%d")
            base_filename = f"podcast_episode_{date_str}"
        else:
            # Remove extension if provided
            base_filename = filename.replace('.txt', '')

        # Handle dict format (both TTS and readable)
        if isinstance(script, dict):
            saved_files = {}

            if 'tts' in script:
                tts_filename = f"{base_filename}_tts.txt"
                with open(tts_filename, "w", encoding="utf-8") as f:
                    f.write(script['tts'])
                print(f"💾 TTS script saved to: {tts_filename}")
                saved_files['tts'] = tts_filename

            if 'readable' in script:
                readable_filename = f"{base_filename}_readable.txt"
                with open(readable_filename, "w", encoding="utf-8") as f:
                    f.write(script['readable'])
                print(f"💾 Readable script saved to: {readable_filename}")
                saved_files['readable'] = readable_filename

            return saved_files

        # Handle string format
        else:
            # Determine format from content or parameter
            if output_format == "tts" or (output_format is None and not script.startswith("=")):
                filename = f"{base_filename}_tts.txt"
            else:
                filename = f"{base_filename}_readable.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(script)

            print(f"💾 Script saved to: {filename}")
            return filename

    def get_tts_segments(self) -> List[Dict[str, str]]:
        """
        Get individual TTS segments with metadata for processing.

        Useful if you want to generate audio for each segment separately
        and then combine them.

        Returns:
            List of dicts with 'type', 'content', and 'speakers' for each segment
        """
        if not self.segment_scripts or not self.framework:
            raise ValueError(
                "No scripts available. Run generate_complete_episode first.")

        segments = []

        # Opening
        segments.append({
            "type": "opening",
            "content": self._extract_dialogue(self.framework["opening"]),
            "speakers": ["Alex", "Sam"]
        })

        # Each content segment with transition
        for i, segment_script in enumerate(self.segment_scripts):
            # Add segment
            segments.append({
                "type": f"segment_{i+1}",
                "content": self._extract_dialogue(segment_script),
                "speakers": ["Alex", "Sam"]
            })

            # Add transition if not last
            if i < len(self.segment_scripts) - 1 and i < len(self.framework["transitions"]):
                segments.append({
                    "type": f"transition_{i+1}",
                    "content": self._extract_dialogue(self.framework["transitions"][i]),
                    "speakers": ["Alex", "Sam"]
                })

        # Closing
        segments.append({
            "type": "closing",
            "content": self._extract_dialogue(self.framework["closing"]),
            "speakers": ["Alex", "Sam"]
        })

        return segments
