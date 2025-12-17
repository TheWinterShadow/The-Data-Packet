"""Unit tests for __about__.py module."""

import unittest

from the_data_packet import __about__


class TestAbout(unittest.TestCase):
    """Test cases for package metadata in __about__.py."""

    def test_version_exists(self):
        """Test that version is defined."""
        self.assertTrue(hasattr(__about__, "__version__"))
        self.assertIsInstance(__about__.__version__, str)
        self.assertRegex(__about__.__version__, r"^\d+\.\d+\.\d+.*$")

    def test_title_exists(self):
        """Test that title is defined."""
        self.assertTrue(hasattr(__about__, "__title__"))
        self.assertIsInstance(__about__.__title__, str)
        self.assertEqual(__about__.__title__, "the_data_packet")

    def test_description_exists(self):
        """Test that description is defined."""
        self.assertTrue(hasattr(__about__, "__description__"))
        self.assertIsInstance(__about__.__description__, str)
        self.assertIn("podcast", __about__.__description__.lower())

    def test_author_exists(self):
        """Test that author information is defined."""
        self.assertTrue(hasattr(__about__, "__author__"))
        self.assertTrue(hasattr(__about__, "__author_email__"))
        self.assertIsInstance(__about__.__author__, str)
        self.assertIsInstance(__about__.__author_email__, str)
        self.assertIn("@", __about__.__author_email__)

    def test_url_exists(self):
        """Test that URL is defined."""
        self.assertTrue(hasattr(__about__, "__url__"))
        self.assertIsInstance(__about__.__url__, str)
        self.assertTrue(__about__.__url__.startswith("http"))

    def test_license_exists(self):
        """Test that license is defined."""
        self.assertTrue(hasattr(__about__, "__license__"))
        self.assertIsInstance(__about__.__license__, str)
        self.assertEqual(__about__.__license__, "MIT")

    def test_version_format(self):
        """Test that version follows semantic versioning."""
        version_parts = __about__.__version__.split(".")
        self.assertGreaterEqual(len(version_parts), 3)
        # Check that major, minor, patch are integers
        for i in range(3):
            self.assertTrue(version_parts[i].isdigit())


if __name__ == "__main__":
    unittest.main()
