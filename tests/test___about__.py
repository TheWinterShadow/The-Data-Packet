"""Tests for __about__.py module."""

import unittest

from the_data_packet import __about__


class TestAbout(unittest.TestCase):
    """Test cases for __about__.py module."""

    def test_version_exists(self):
        """Test that __version__ is defined."""
        self.assertTrue(hasattr(__about__, '__version__'))
        self.assertIsInstance(__about__.__version__, str)
        self.assertNotEqual(__about__.__version__, '')

    def test_title_exists(self):
        """Test that __title__ is defined."""
        self.assertTrue(hasattr(__about__, '__title__'))
        self.assertEqual(__about__.__title__, 'the-data-packet')

    def test_author_exists(self):
        """Test that __author__ is defined."""
        self.assertTrue(hasattr(__about__, '__author__'))
        self.assertIsInstance(__about__.__author__, str)

    def test_email_exists(self):
        """Test that __email__ is defined."""
        self.assertTrue(hasattr(__about__, '__email__'))
        self.assertIsInstance(__about__.__email__, str)

    def test_description_exists(self):
        """Test that __description__ is defined."""
        self.assertTrue(hasattr(__about__, '__description__'))
        self.assertIsInstance(__about__.__description__, str)


if __name__ == '__main__':
    unittest.main()
