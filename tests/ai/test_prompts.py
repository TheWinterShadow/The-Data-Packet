"""Tests for prompts module."""

import unittest

from the_data_packet.ai.prompts import ARTICLE_TO_SEGMENT_PROMPT, SUMMARIES_TO_FRAMEWORK_PROMPT


class TestPrompts(unittest.TestCase):
    """Test cases for prompts module."""

    def test_podcast_script_prompt_exists(self):
        """Test that PODCAST_SCRIPT_PROMPT is defined."""
        self.assertIsInstance(PODCAST_SCRIPT_PROMPT, str)
        self.assertGreater(len(PODCAST_SCRIPT_PROMPT), 100)

    def test_podcast_script_prompt_contains_placeholders(self):
        """Test that PODCAST_SCRIPT_PROMPT contains expected placeholders."""
        expected_placeholders = [
            '{show_name}',
            '{episode_date}',
            '{articles}'
        ]

        for placeholder in expected_placeholders:
            self.assertIn(placeholder, PODCAST_SCRIPT_PROMPT)

    def test_script_analysis_prompt_exists(self):
        """Test that SCRIPT_ANALYSIS_PROMPT is defined."""
        self.assertIsInstance(SCRIPT_ANALYSIS_PROMPT, str)
        self.assertGreater(len(SCRIPT_ANALYSIS_PROMPT), 50)

    def test_script_analysis_prompt_contains_placeholders(self):
        """Test that SCRIPT_ANALYSIS_PROMPT contains expected placeholders."""
        expected_placeholders = ['{script}']

        for placeholder in expected_placeholders:
            self.assertIn(placeholder, SCRIPT_ANALYSIS_PROMPT)

    def test_prompts_are_non_empty(self):
        """Test that prompts are not empty strings."""
        self.assertNotEqual(PODCAST_SCRIPT_PROMPT.strip(), '')
        self.assertNotEqual(SCRIPT_ANALYSIS_PROMPT.strip(), '')

    def test_prompts_formatting(self):
        """Test that prompts can be formatted with sample data."""
        # Test PODCAST_SCRIPT_PROMPT formatting
        test_data = {
            'show_name': 'Test Show',
            'episode_date': 'January 1, 2024',
            'articles': 'Sample article content'
        }

        formatted_prompt = PODCAST_SCRIPT_PROMPT.format(**test_data)
        self.assertIn('Test Show', formatted_prompt)
        self.assertIn('January 1, 2024', formatted_prompt)
        self.assertIn('Sample article content', formatted_prompt)

        # Test SCRIPT_ANALYSIS_PROMPT formatting
        script_data = {'script': 'Sample script content'}
        formatted_script_prompt = SCRIPT_ANALYSIS_PROMPT.format(**script_data)
        self.assertIn('Sample script content', formatted_script_prompt)


if __name__ == '__main__':
    unittest.main()
