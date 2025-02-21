from pymilvus import connections
from config import get_settings
from .migrations import create_collection_if_not_exists

settings = get_settings()

# Initialize Milvus connection
connections.connect(
    alias="default", 
    host=settings.MILVUS_HOST,
    port=settings.MILVUS_PORT
)

# Run migrations and get collection
collection = create_collection_if_not_exists()
