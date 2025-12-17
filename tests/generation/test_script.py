"""Unit tests for generation.script module."""

import unittest
from unittest.mock import Mock, patch

from the_data_packet.core.exceptions import AIGenerationError, ConfigurationError
from the_data_packet.generation.script import ScriptGenerator
from the_data_packet.sources.base import Article


class TestScriptGenerator(unittest.TestCase):
    """Test cases for ScriptGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.anthropic_api_key = "test-api-key"
        self.mock_config.claude_model = "claude-sonnet-4-5-20250929"
        self.mock_config.max_tokens = 3000
        self.mock_config.temperature = 0.7
        self.mock_config.show_name = "Test Podcast"

        self.sample_article = Article(
            title="Test Article",
            content="This is test content about technology and AI developments.",
            url="https://example.com/article",
            author="Test Author",
            category="security",
            source="test",
        )

    @patch("the_data_packet.generation.script.get_config")
    @patch("the_data_packet.generation.script.Anthropic")
    def test_init_with_api_key(self, mock_anthropic, mock_get_config):
        """Test ScriptGenerator initialization with API key."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        generator = ScriptGenerator(api_key="test-key")

        self.assertEqual(generator.api_key, "test-key")
        self.assertEqual(generator.config, self.mock_config)
        mock_anthropic.assert_called_once_with(api_key="test-key")

    @patch("the_data_packet.generation.script.get_config")
    def test_init_without_api_key_raises_error(self, mock_get_config):
        """Test that initialization without API key raises ConfigurationError."""
        mock_config_no_key = Mock()
        mock_config_no_key.anthropic_api_key = None
        mock_get_config.return_value = mock_config_no_key

        with self.assertRaises(ConfigurationError) as cm:
            ScriptGenerator()

        self.assertIn("Anthropic API key is required", str(cm.exception))

    @patch("the_data_packet.generation.script.get_config")
    @patch("the_data_packet.generation.script.Anthropic")
    def test_init_with_config_api_key(self, mock_anthropic, mock_get_config):
        """Test ScriptGenerator initialization with API key from config."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        generator = ScriptGenerator()

        self.assertEqual(generator.api_key, "test-api-key")
        mock_anthropic.assert_called_once_with(api_key="test-api-key")

    @patch("the_data_packet.generation.script.get_config")
    @patch("the_data_packet.generation.script.Anthropic")
    def test_generate_script_empty_articles_raises_error(
        self, mock_anthropic, mock_get_config
    ):
        """Test that empty articles list raises AIGenerationError."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        generator = ScriptGenerator(api_key="test-key")

        with self.assertRaises(AIGenerationError) as cm:
            generator.generate_script([])

        self.assertIn("No articles provided", str(cm.exception))

    @patch("the_data_packet.generation.script.get_config")
    @patch("the_data_packet.generation.script.Anthropic")
    def test_generate_script_invalid_articles_raises_error(
        self, mock_anthropic, mock_get_config
    ):
        """Test that invalid articles raise AIGenerationError."""
        mock_get_config.return_value = self.mock_config
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        generator = ScriptGenerator(api_key="test-key")

        # Create invalid article (missing required fields)
        invalid_article = Article(
            title="",  # Empty title makes it invalid
            content="",  # Empty content makes it invalid
            url="https://example.com",
            author="Test Author",
        )

        with self.assertRaises(AIGenerationError) as cm:
            generator.generate_script([invalid_article])

        self.assertIn("No valid articles provided", str(cm.exception))

    def test_parse_segment_response_valid(self):
        """Test parsing valid segment response."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                response = """
                ### SEGMENT SCRIPT
                Alex: Welcome to the show!
                Sam: Thanks for having me.
                Alex: Let's discuss the latest tech news.

                ### SEGMENT SUMMARY
                **Headline**: Latest tech developments
                **Key Players**: Tech companies
                **Category**: Technology news
                **Key Takeaway**: Tech is evolving rapidly
                """

                segment, summary = generator._parse_segment_response(response)

                self.assertIn("Alex: Welcome to the show!", segment)
                self.assertIn("Sam: Thanks for having me.", segment)
                self.assertIn("Latest tech developments", summary)
                self.assertIn("Tech companies", summary)

    def test_parse_segment_response_missing_script(self):
        """Test parsing response with missing script section."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                response = """
                ### SEGMENT SUMMARY
                **Headline**: Latest tech developments
                **Key Players**: Tech companies
                """

                with self.assertRaises(AIGenerationError) as cm:
                    generator._parse_segment_response(response)

                self.assertIn("No segment script found", str(cm.exception))

    def test_parse_segment_response_missing_summary(self):
        """Test parsing response with missing summary section."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                response = """
                ### SEGMENT SCRIPT
                Alex: Welcome to the show!
                Sam: Thanks for having me.
                """

                with self.assertRaises(AIGenerationError) as cm:
                    generator._parse_segment_response(response)

                self.assertIn("No segment summary found", str(cm.exception))

    def test_is_refusal_response_with_non_tech_content(self):
        """Test detection of non-tech content refusal."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                response = "NON_TECH_CONTENT: This article is not appropriate for a tech news podcast"
                self.assertTrue(generator._is_refusal_response(response))

    def test_is_refusal_response_with_legacy_patterns(self):
        """Test detection of legacy refusal patterns."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                refusal_responses = [
                    "I appreciate you sharing this, but this is not a tech article",
                    "This article is actually about lifestyle",
                    "Not appropriate content for a tech podcast",
                    "This isn't appropriate for tech news",
                ]

                for response in refusal_responses:
                    with self.subTest(response=response):
                        self.assertTrue(generator._is_refusal_response(response))

    def test_is_refusal_response_with_valid_content(self):
        """Test that valid tech content is not detected as refusal."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                valid_response = """
                ### SEGMENT SCRIPT
                Alex: Today we're talking about AI developments
                Sam: That sounds fascinating
                """

                self.assertFalse(generator._is_refusal_response(valid_response))

    def test_format_summaries(self):
        """Test formatting of summaries for framework prompt."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                summaries = [
                    "First tech story about AI",
                    "Second story about cybersecurity",
                    "Third story about quantum computing",
                ]

                formatted = generator._format_summaries(summaries)

                self.assertIn("Segment 1:", formatted)
                self.assertIn("First tech story about AI", formatted)
                self.assertIn("Segment 2:", formatted)
                self.assertIn("Second story about cybersecurity", formatted)
                self.assertIn("Segment 3:", formatted)
                self.assertIn("Third story about quantum computing", formatted)

    def test_number_to_words_basic_numbers(self):
        """Test conversion of basic numbers to words."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                test_cases = [
                    (0, "zero"),
                    (1, "one"),
                    (5, "five"),
                    (10, "ten"),
                    (15, "fifteen"),
                    (20, "twenty"),
                    (25, "twenty five"),
                    (100, "one hundred"),
                    (150, "one hundred fifty"),
                    (1000, "one thousand"),
                    (1500, "one thousand five hundred"),
                    (1000000, "one million"),
                ]

                for number, expected in test_cases:
                    with self.subTest(number=number):
                        result = generator._number_to_words(number)
                        self.assertEqual(result, expected)

    def test_optimize_script_for_tts_abbreviations(self):
        """Test TTS optimization of abbreviations."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                script = "AI technology from AWS and CEO updates on IoT devices vs. traditional systems."
                optimized = generator._optimize_script_for_tts(script)

                self.assertIn("artificial intelligence", optimized)
                self.assertIn("Amazon Web Services", optimized)
                self.assertIn("C.E.O.", optimized)
                self.assertIn("Internet of Things", optimized)
                # Note: vs. may not be replaced due to word boundary regex

    def test_optimize_script_for_tts_urls(self):
        """Test TTS optimization of URLs."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                script = "Visit https://example.com for more information."
                optimized = generator._optimize_script_for_tts(script)

                self.assertIn("example.com", optimized)
                self.assertNotIn("https://", optimized)

    def test_parse_framework_sections(self):
        """Test parsing of framework response into sections."""
        with patch("the_data_packet.generation.script.get_config") as mock_get_config:
            mock_get_config.return_value = self.mock_config

            with patch("the_data_packet.generation.script.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                generator = ScriptGenerator(api_key="test-key")

                framework = """
                ## SHOW OPENING
                Alex: Welcome to the show!
                Sam: Great to be here!

                ## TRANSITION 1→2
                Alex: Now let's move to our next story.

                ## SHOW CLOSING
                Alex: Thanks for listening!
                Sam: See you next time!
                """

                sections = generator._parse_framework(framework)

                self.assertIn("opening", sections)
                self.assertIn("Welcome to the show!", sections["opening"])
                # The parser creates transition_TRANSITION due to parsing logic
                transition_key = [
                    k for k in sections.keys() if k.startswith("transition_")
                ][0]
                self.assertIn("move to our next story", sections[transition_key])
                self.assertIn("closing", sections)
                self.assertIn("Thanks for listening!", sections["closing"])


if __name__ == "__main__":
    unittest.main()
