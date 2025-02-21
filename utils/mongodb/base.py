from pymongo import MongoClient
from config import get_settings
from .migrations import create_collection_if_not_exists

# Run migrations and get collection
collection = create_collection_if_not_exists()
