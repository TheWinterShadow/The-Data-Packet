"""Tests for the MongoDB utility client."""

import unittest
from unittest.mock import Mock, patch

from the_data_packet.utils.mongodb import MongoDBClient


class TestMongoDBClient(unittest.TestCase):
    """Test cases for the MongoDBClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.username = "test_user"
        self.password = "test_password"
        self.test_collection = "test_collection"
        self.test_document = {"_id": "123", "name": "test", "value": 42}

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_init_creates_client_and_database(self, mock_mongo_client):
        """Test that initialization creates MongoDB client and database connection."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_client_instance.the_data_packet = mock_database
        mock_mongo_client.return_value = mock_client_instance

        client = MongoDBClient(self.username, self.password)

        # Verify MongoClient was called with correct connection string and timeout
        expected_connection_string = (
            f"mongodb://{self.username}:{self.password}@127.0.0.1:27017/"
            f"the_data_packet?authSource=admin"
        )
        mock_mongo_client.assert_called_once_with(
            expected_connection_string, serverSelectionTimeoutMS=5000
        )

        # Verify client and database are set correctly
        self.assertEqual(client.client, mock_client_instance)
        self.assertEqual(client.db, mock_database)

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_get_collection_returns_collection(self, mock_mongo_client):
        """Test that get_collection returns the correct collection."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_collection = Mock()

        mock_client_instance.the_data_packet = mock_database
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_mongo_client.return_value = mock_client_instance

        client = MongoDBClient(self.username, self.password)
        collection = client.get_collection(self.test_collection)

        # Verify database access was called correctly
        mock_database.__getitem__.assert_called_once_with(self.test_collection)
        self.assertEqual(collection, mock_collection)

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_insert_document_calls_collection_insert_one(self, mock_mongo_client):
        """Test that insert_document calls the collection's insert_one method."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_collection = Mock()
        mock_insert_result = Mock()

        mock_client_instance.the_data_packet = mock_database
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_collection.insert_one.return_value = mock_insert_result
        mock_mongo_client.return_value = mock_client_instance

        client = MongoDBClient(self.username, self.password)
        result = client.insert_document(self.test_collection, self.test_document)

        # Verify insert_one was called with correct document
        mock_collection.insert_one.assert_called_once_with(self.test_document)
        self.assertEqual(result, mock_insert_result)

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_find_documents_calls_collection_find(self, mock_mongo_client):
        """Test that find_documents calls the collection's find method."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_collection = Mock()
        mock_cursor = Mock()

        mock_client_instance.the_data_packet = mock_database
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_collection.find.return_value = mock_cursor
        mock_mongo_client.return_value = mock_client_instance

        query = {"name": "test"}
        client = MongoDBClient(self.username, self.password)
        result = client.find_documents(self.test_collection, query)

        # Verify find was called with correct query
        mock_collection.find.assert_called_once_with(query)
        self.assertEqual(result, mock_cursor)

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_find_documents_with_none_query(self, mock_mongo_client):
        """Test that find_documents handles None query by using empty dict."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_collection = Mock()
        mock_cursor = Mock()

        mock_client_instance.the_data_packet = mock_database
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_collection.find.return_value = mock_cursor
        mock_mongo_client.return_value = mock_client_instance

        client = MongoDBClient(self.username, self.password)
        result = client.find_documents(self.test_collection, None)

        # Verify find was called with empty dict when query is None
        mock_collection.find.assert_called_once_with({})
        self.assertEqual(result, mock_cursor)

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_find_documents_with_empty_query(self, mock_mongo_client):
        """Test that find_documents works with empty query."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_collection = Mock()
        mock_cursor = Mock()

        mock_client_instance.the_data_packet = mock_database
        mock_database.__getitem__ = Mock(return_value=mock_collection)
        mock_collection.find.return_value = mock_cursor
        mock_mongo_client.return_value = mock_client_instance

        client = MongoDBClient(self.username, self.password)
        result = client.find_documents(self.test_collection, {})

        # Verify find was called with empty dict
        mock_collection.find.assert_called_once_with({})
        self.assertEqual(result, mock_cursor)

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_close_calls_client_close(self, mock_mongo_client):
        """Test that close calls the client's close method."""
        mock_client_instance = Mock()
        mock_database = Mock()

        mock_client_instance.the_data_packet = mock_database
        mock_mongo_client.return_value = mock_client_instance

        client = MongoDBClient(self.username, self.password)
        client.close()

        # Verify client.close was called
        mock_client_instance.close.assert_called_once()

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_connection_string_format(self, mock_mongo_client):
        """Test that the MongoDB connection string is formatted correctly."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_client_instance.the_data_packet = mock_database
        mock_mongo_client.return_value = mock_client_instance

        # Test with special characters in password
        special_username = "user@domain.com"
        special_password = "p@ssw0rd!#$"

        MongoDBClient(special_username, special_password)

        expected_connection_string = (
            f"mongodb://{special_username}:{special_password}@127.0.0.1:27017/"
            f"the_data_packet?authSource=admin"
        )
        mock_mongo_client.assert_called_once_with(
            expected_connection_string, serverSelectionTimeoutMS=5000
        )

    @patch("the_data_packet.utils.mongodb.MongoClient")
    def test_database_name_consistency(self, mock_mongo_client):
        """Test that the database name is consistently 'the_data_packet'."""
        mock_client_instance = Mock()
        mock_database = Mock()
        mock_client_instance.the_data_packet = mock_database
        mock_mongo_client.return_value = mock_client_instance

        client = MongoDBClient(self.username, self.password)

        # Verify the database attribute is set to the correct database
        self.assertEqual(client.db, mock_database)
        # Verify that the database access was for 'the_data_packet'
        self.assertEqual(client.db, mock_client_instance.the_data_packet)


if __name__ == "__main__":
    unittest.main()
