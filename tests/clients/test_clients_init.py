"""Tests for clients package __init__.py module."""

import unittest


class TestClientsInit(unittest.TestCase):
    """Test cases for clients package __init__.py module."""

    def test_clients_module_imports(self):
        """Test that clients module classes are importable."""
        from the_data_packet.clients import HTTPClient, RSSClient

        self.assertIsNotNone(HTTPClient)
        self.assertIsNotNone(RSSClient)

    def test_clients_module_all_exports(self):
        """Test clients module __all__ exports."""
        import the_data_packet.clients as clients_module

        if hasattr(clients_module, '__all__'):
            expected_exports = ['HTTPClient', 'RSSClient']
            for export in expected_exports:
                self.assertIn(export, clients_module.__all__)


if __name__ == '__main__':
    unittest.main()
