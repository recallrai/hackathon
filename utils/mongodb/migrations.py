from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError
from config import get_settings

settings = get_settings()

def create_collection_if_not_exists() -> Collection:
    """Create MongoDB database and collection if they don't exist.
    Format of data stored in MongoDB:
    {
        _id: str,  # document_id 
        adjacency_list: {
            node_id: [node_id1, node_id2, ...],
            ...
        }
    }
    """
    try:
        client = MongoClient(settings.get_mongo_uri(), serverSelectionTimeoutMS=5000)
        # Ping server to check connection
        client.admin.command('ping')
    except ServerSelectionTimeoutError:
        raise ConnectionError(f"Could not connect to MongoDB at {settings.get_mongo_uri()}")

    # Create database if it doesn't exist
    # In MongoDB, creating a database is implicit when creating first collection
    db = client[settings.MONGO_DB]

    # Create collection if it doesn't exist
    if settings.MONGO_COLLECTION not in db.list_collection_names():
        collection = db.create_collection(settings.MONGO_COLLECTION)

        # Create indexes
        collection.create_index([("_id", ASCENDING)])

        # Insert initial empty document to ensure database creation
        collection.insert_one({"_id": "schema_version", "version": 1})

        return collection

    return db[settings.MONGO_COLLECTION]
