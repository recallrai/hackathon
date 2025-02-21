from typing import Dict, List
from .base import collection

def search_relevent_nodes_by_embeddings(
    embeddings: List[List[float]], 
    min_top_k: int = 5, 
    # max_top_k: int = -1, 
    threshold: float = 0.75
) -> Dict[str, str]:
    """Search for relevant nodes by embeddings using cosine similarity.

    This function searches through a vector database to find the most similar nodes
    based on the input embeddings vector.

    Args:
        embeddings (List[List[float]]): Input embeddings vector to search against
        min_top_k (int, optional): Minimum number of results to return. Defaults to 5.
        # max_top_k (int, optional): Maximum number of results to return. Defaults to -1.
        threshold (float, optional): Similarity threshold to filter results. Defaults to 0.5.
            All nodes with similarity scores above this threshold will be returned.
            This will override the max_top_k parameter.
            If number of nodes that exceed the threshold is less than min_top_k,
            we'll return at least min_top_k results.

    Returns:
        Dict[str, str]: List of node IDs with similarity scores that
            exceed the similarity threshold, ordered by decreasing similarity score.
            Returns min_top_k to max_top_k results.
            If similarity threshold is set, returns all nodes that exceed the threshold.

    Example:
        >>> embeddings = [[0.1, 0.2, 0.3, 0.4]]
        >>> results = search_relevent_nodes_by_embeddings(embeddings)
        >>> print(results)
        {'node_123': 0.8, 'node_456': 0.7, 'node_789': 0.6}
    """

    # Search parameters
    search_params = {
        "metric_type": "COSINE",
        "params": {"nprobe": 10},
    }

    # Search collection
    results = collection.search(
        data=embeddings,
        anns_field="embedding",
        param=search_params,
        # limit=max_top_k,
        limit=1000,
        expr=None,
        output_fields=["node_id"]
    )

    # Filter by threshold and return node IDs with scores
    matches = {}
    for hit in results[0]:
        # Add to matches if similarity score exceeds threshold
        if hit.score >= threshold:
            matches[hit.entity.get("node_id")] = hit.score
        # if max_top_k != -1 and len(matches) >= max_top_k:
        #     break

    # Ensure minimum results
    if len(matches) < min_top_k:
        for hit in results[0][:min_top_k]:
            node_id = hit.entity.get("node_id")
            if node_id not in matches:
                matches[node_id] = hit.score

    return matches

def insert_node(node_id: str, embeddings: List[List[float]]) -> None:
    """Insert a node into the database.

    This function inserts a node into the vector database with the given node ID and embeddings.
    
    Args:
        node_id (str): Unique identifier for the node.
        embeddings (List[float]): Vector representation of the node content.

    Returns:
        None

    Example:
        >>> node_id = 'node_123'
        >>> embeddings = [0.1, 0.2, 0.3, 0.4]
        >>> insert_node(node_id, embeddings)
    """
    # Insert node into collection
    collection.insert([
        {
            "node_id": node_id,
            "embedding": embeddings[0]
        }
    ])

def update_embeddings(node_id: str, embeddings: List[float]) -> None:
    """Update a node's embeddings in the database.

    This function updates the embeddings of an existing node in the vector database
    and ensures the index is properly updated.

    Args:
        node_id (str): Unique identifier for the node.
        embeddings (List[float]): New vector representation of the node content.

    Returns:
        None
    """
    # Update node in collection
    # collection.update(
    #     {"node_id": node_id},
    #     {"embedding": embeddings}
    # )
    collection.upsert(
        [
            {
                "node_id": node_id,
                "embedding": embeddings
            }
        ]
    )
    
    # Ensure changes are persisted and index is updated
    refresh_collection()

def clear_all_nodes() -> None:
    """Clear all nodes from the database.

    This function removes all nodes from the vector database.

    Returns:
        None

    Example:
        >>> clear_all_nodes()
    """
    try:
        # Delete all entries where node_id exists (all entries)
        collection.delete("node_id != ''")
        # Ensure changes are persisted
        collection.flush()
    except Exception as e:
        # print(f"Error clearing nodes: {str(e)}")
        raise

def get_node_count() -> int:
    """Get total number of nodes in Milvus"""
    refresh_collection()
    return collection.num_entities

def refresh_collection() -> None:
    """Refresh collection to apply changes"""
    collection.flush()
    collection.load()
