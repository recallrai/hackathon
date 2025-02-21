from typing import Dict, List
from .base import collection

DOC_ID = "32f7543c-cf51-49f1-8163-93652e26a695"

def make_edge(
    node1_id: str,
    node2_id: str,
    doc_id: str = DOC_ID,
) -> None:
    """Update the adjacency list in MongoDB to add an edge between two nodes.
    As the graph is undirected, the edge is added to both nodes.
    
    This function updates the adjacency list in MongoDB to add an edge between two nodes.
    
    Args:
        doc_id (str): ID of the document.
        node1_id (str): ID of the first node.
        node2_id (str): ID of the second node.

    Returns:
        None

    Example:
        >>> node1_id = 'node_123'
        >>> node2_id = 'node_456'
        >>> make_edge(node1_id, node2_id)
    """
    collection.update_one(
        {"_id": doc_id},
        {
            "$set": {"_id": doc_id},  # Ensures document exists
            "$addToSet": {
                f"adjacency_list.{node1_id}": node2_id,
                f"adjacency_list.{node2_id}": node1_id,
            }
        },
        upsert=True  # Create document if it doesn't exist
    )

# def delete_edge(
#     doc_id: str,
#     node1_id: str,
#     node2_id: str,
# ) -> None:
#     """Update the adjacency list in MongoDB to remove an edge between two nodes.
#     As the graph is undirected, the edge is removed from both nodes.

#     This function updates the adjacency list in MongoDB to remove an edge between two nodes.

#     Args:
#         doc_id (str): ID of the document.
#         node1_id (str): ID of the first node.
#         node2_id (str): ID of the second node.

#     Returns:
#         None

#     Example:
#         >>> node1_id = 'node_123'
#         >>> node2_id = 'node_456'
#         >>> delete_edge(node1_id, node2_id)
#     """
#     pass

def get_neighbors(
    node_id: str,
    doc_id: str = DOC_ID,
) -> List[str]:
    """Get the neighbors of a node from the adjacency list in MongoDB.
    
    This function retrieves the neighbors of a node from the adjacency list in MongoDB.
    
    Args:
        doc_id (str): ID of the document
        node_id (str): ID of the node.

    Returns:
        List[str]: List of node IDs that are neighbors of the given node.

    Example:
        >>> node_id = 'node_123'
        >>> neighbors = get_neighbors(node_id)
        >>> print(neighbors)
        ['node_456', 'node_789']
    """
    doc = collection.find_one({"_id": doc_id})
    return doc["adjacency_list"].get(node_id, [])

def get_n_hop_neighbors(
    node_id: str,
    n: int,
    doc_id: str = DOC_ID,
) -> List[str]:
    """Get the n-hop neighbors of a node from the adjacency list in MongoDB.
    
    This function retrieves the n-hop neighbors of a node from the adjacency list in MongoDB.
    
    Args:
        doc_id (str): ID of the document.
        node_id (str): ID of the node.
        n (int): Number of hops to consider.

    Returns:
        List[str]: List of node IDs that are n-hop neighbors of the given node.

    Example:
        >>> node_id = 'node_123'
        >>> n = 2
        >>> n_hop_neighbors = get_n_hop_neighbors(node_id, n)
        >>> print(n_hop_neighbors)
        ['node_456', 'node_789', 'node_101', 'node_202']
    """
    # use get_neighbors recursively to get n-hop neighbors
    visited = set([node_id])
    current_nodes = {node_id}
    
    for _ in range(n):
        next_nodes = set()
        for node in current_nodes:
            neighbors = get_neighbors(doc_id, node)
            next_nodes.update(set(neighbors) - visited)
        visited.update(next_nodes)
        current_nodes = next_nodes
    
    return list(visited - {node_id})

def get_adjacency_list(
    doc_id: str = DOC_ID,
) -> Dict[str, List[str]]:
    """Get the adjacency list from MongoDB for a given document.
    
    This function retrieves the adjacency list from MongoDB for a given document.
    
    Args:
        doc_id (str): ID of the document.

    Returns:
        Dict[str, List[str]]: Adjacency list of the document.

    Example:
        >>> doc_id = 'doc_123'
        >>> adjacency_list = get_adjacency_list(doc_id)
        >>> print(adjacency_list)
        {
            'node_123': ['node_456', 'node_789'],
            'node_456': ['node_123', 'node_789'],
            'node_789': ['node_123', 'node_456']
        }
    """
    doc = collection.find_one({"_id": doc_id})
    if doc is None:
        return {}
    return doc.get("adjacency_list", {})

def delete_adjacency_list(
    doc_id: str = DOC_ID,
) -> None:
    """Delete the adjacency list from MongoDB for a given document.
    
    This function deletes the adjacency list from MongoDB for a given document.
    
    Args:
        doc_id (str): ID of the document.

    Returns:
        None

    Example:
        >>> doc_id = 'doc_123'
        >>> delete_adjacency_list(doc_id)
    """
    # collection.delete_one({"_id": doc_id})
    collection.update_one(
        {"_id": doc_id},
        {"$unset": {"adjacency_list": ""}}
    )
