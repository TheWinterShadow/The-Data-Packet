"""Unit tests for utils.__init__.py module."""

import unittest

from the_data_packet.utils import HTTPClient, S3Storage, S3UploadResult


class TestUtilsInit(unittest.TestCase):
    """Test cases for utils module initialization."""

    def test_all_imports_available(self):
        """Test that all expected utilities are importable."""
        # Test that classes exist and are importable
        self.assertIsNotNone(HTTPClient)
        self.assertIsNotNone(S3Storage)
        self.assertIsNotNone(S3UploadResult)

    def test_classes_are_callable(self):
        """Test that imported utilities are actually classes."""
        self.assertTrue(callable(HTTPClient))
        self.assertTrue(callable(S3Storage))
        self.assertTrue(callable(S3UploadResult))

    def test_module_all_attribute(self):
        """Test that __all__ attribute contains expected items."""
        import the_data_packet.utils as utils_module

        expected_items = ["HTTPClient", "S3Storage", "S3UploadResult"]

        self.assertTrue(hasattr(utils_module, "__all__"))
        for item in expected_items:
            self.assertIn(item, utils_module.__all__)

    def test_import_structure(self):
        """Test that utilities come from expected modules."""
        # Test that we can access the utilities as expected
        from the_data_packet.utils.http import HTTPClient as HTTPClientDirect
        from the_data_packet.utils.s3 import S3Storage as S3StorageDirect
        from the_data_packet.utils.s3 import S3UploadResult as S3UploadResultDirect

        # Should be the same classes
        self.assertIs(HTTPClient, HTTPClientDirect)
        self.assertIs(S3Storage, S3StorageDirect)
        self.assertIs(S3UploadResult, S3UploadResultDirect)


if __name__ == "__main__":
    unittest.main()
