import os
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult

from the_data_packet.core.logging import get_logger

logger = get_logger(__name__)


class MongoDBClient:
    """A MongoDB client wrapper for database operations.

    This class provides a simplified interface for connecting to MongoDB
    and performing common database operations like inserting and querying documents.

    Attributes:
        client (MongoClient): The MongoDB client instance.
        db (Database): The MongoDB database instance.
    """

    def __init__(self, username: str, password: str) -> None:
        """Initialize the MongoDB client.

        Args:
            username (str): The username for MongoDB authentication.
            password (str): The password for MongoDB authentication.
        """
        # Determine MongoDB host - use host.docker.internal in Docker, localhost otherwise
        mongodb_host = os.getenv("MONGODB_HOST", "127.0.0.1")

        connection_string = f"mongodb://{username}:{password}@{mongodb_host}:27017/the_data_packet?authSource=admin"
        logger.info(
            f"Attempting MongoDB connection to: mongodb://{username}:***@{mongodb_host}:27017/the_data_packet?authSource=admin"  # noqa: E501
        )
        logger.info(
            f"Environment check - MONGODB_HOST: {os.getenv('MONGODB_HOST', 'not set')}"
        )
        logger.info(f"Docker environment detected: {os.path.exists('/.dockerenv')}")

        try:
            self.client: MongoClient = MongoClient(
                connection_string, serverSelectionTimeoutMS=5000
            )
            # Test the connection
            self.client.admin.command("ping")
            logger.info("MongoDB connection successful!")
            self.db: Database = self.client.the_data_packet
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            logger.error(
                f"Connection string used: mongodb://{username}:***@{mongodb_host}:27017/the_data_packet?authSource=admin"  # noqa: E501
            )
            raise

    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection instance.
        """
        return self.db[collection_name]

    def insert_document(
        self, collection_name: str, document: Dict[str, Any]
    ) -> InsertOneResult:
        """Insert a single document into a collection.

        Args:
            collection_name (str): The name of the collection to insert into.
            document (Dict[str, Any]): The document to insert.

        Returns:
            InsertOneResult: The result of the insert operation, containing
                           information about the insertion including the inserted_id.
        """
        try:
            logger.debug(f"Inserting document into collection '{collection_name}'")
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            logger.debug(
                f"Document inserted successfully with ID: {result.inserted_id}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Failed to insert document into collection '{collection_name}': {e}"
            )
            raise

    def find_documents(
        self, collection_name: str, query: Optional[Dict[str, Any]] = None
    ) -> Cursor:
        """Find documents in a collection based on a query.

        Args:
            collection_name (str): The name of the collection to search in.
            query (Optional[Dict[str, Any]]): The query filter. If None or empty,
                                            returns all documents in the collection.

        Returns:
            Cursor: A cursor object that can be iterated over to access
                   the matching documents.
        """
        try:
            logger.debug(f"Querying collection '{collection_name}' with query: {query}")
            collection = self.get_collection(collection_name)
            if query is None:
                query = {}
            cursor = collection.find(query)
            logger.debug("Query executed successfully")
            return cursor
        except Exception as e:
            logger.error(f"Failed to query collection '{collection_name}': {e}")
            raise

    def close(self) -> None:
        """Close the MongoDB client connection.

        This should be called when the client is no longer needed
        to properly close the connection and free resources.
        """
        logger.debug("Closing MongoDB connection")
        self.client.close()
        logger.debug("MongoDB connection closed")
