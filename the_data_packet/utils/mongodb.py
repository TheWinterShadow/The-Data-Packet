from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult


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
        self.client: MongoClient = MongoClient(
            f"mongodb://{username}:{password}@localhost:27017/the_data_packet?authSource=admin"
        )
        self.db: Database = self.client.the_data_packet

    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection instance.
        """
        return self.db[collection_name]

    def close(self) -> None:
        """Close the MongoDB client connection.

        This should be called when the client is no longer needed
        to properly close the connection and free resources.
        """
        self.client.close()

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
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

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
        collection = self.get_collection(collection_name)
        if query is None:
            query = {}
        return collection.find(query)
