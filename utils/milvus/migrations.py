from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, MilvusClient
from config import get_settings

settings = get_settings()

def create_collection_if_not_exists() -> Collection:
    """Create Milvus collection and index if they don't exist.

    Format of data stored in Milvus:
        | Field      | Type           | Description                      |
        |------------|----------------|----------------------------------|
        | node_id    | str            | Unique identifier for each node  |
        | embedding  | float[emd_dim] | Vector representation of content |
    """

    # Define collection schema
    fields = [
        FieldSchema(name="node_id", dtype=DataType.VARCHAR, max_length=200, is_primary=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.embedding_model.n_dim)
    ]

    schema = CollectionSchema(
        fields=fields,
        description="Stores text embeddings for semantic search"
    )

    # Create collection if it doesn't exist
    client = MilvusClient(
        uri=f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}"
    )
    if not client.list_collections():
        collection = Collection(
            name=settings.MILVUS_COLLECTION,
            schema=schema,
            using='default'
        )

        # Create index for vector field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

        collection.load()
        return collection

    return Collection(settings.MILVUS_COLLECTION)
