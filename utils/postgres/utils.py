from typing import List
from sqlalchemy.orm import Session
from .base import get_db
from .schemas import NodesDb, TagsDb, NodesTagsDb
from utils.models import Memory
from datetime import datetime, timezone
import uuid

def get_memory_details(
    node_id: str,
) -> Memory:
    """Get the details of a memory from the database.
    
    This function retrieves the details of a memory from the database.
    
    Args:
        node_id (str): ID of the memory.
    
    Returns:
        Memory: Details of the memory.
    
    Example:
        >>> node_id = 'node_123'
        >>> get_memory_details(node_id)
    """
    db: Session = next(get_db())
    
    # Get node details
    node = (
        db.query(NodesDb)
        .filter(NodesDb.id == node_id)
        .first()
    )
    
    # Get tags
    # tag_ids = db.query(NodesTagsDb.tag_id).filter(
    #     NodesTagsDb.node_id == node_id
    # ).all()
    # tag_ids = [t[0] for t in tag_ids]
    
    # tags = db.query(TagsDb.name).filter(
    #     TagsDb.id.in_(tag_ids)
    # ).all()
    # tags = [t[0] for t in tags]
    print(node)
    return Memory(
        id=node.id,
        content=node.text,
        # tags=tags,
        created_at=str(node.created_at)
    )

def insert_memory(
    text: str,
) -> str:
    """Insert a memory node into the database.
    
    This function inserts a memory node into the database.
    
    Args:
        text (str): Text of the memory.
    
    Returns:
        str: ID of the inserted memory node.
    
    Example:
        >>> text = 'This is a memory.'
        >>> db = next(get_db())
        >>> insert_node(text, db)
    """
    # Get database session
    db: Session = next(get_db())
    
    # Insert node
    node = NodesDb(
        id=str(uuid.uuid4()),
        text=text,
        created_at=datetime.now(timezone.utc)
    )
    try:
        db.add(node)
        db.commit()
        db.refresh(node)
    except Exception as e:
        db.rollback()
        raise e

    return node.id

def clear_all_nodes() -> None:
    """Clear all nodes from the database.
    
    This function removes all nodes from the database.
    
    Returns:
        None
    
    Example:
        >>> clear_all_nodes()
    """
    db: Session = next(get_db())
    
    try:
        db.query(NodesDb).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def get_node_count() -> int:
    """Get total number of nodes in PostgreSQL"""
    db = next(get_db())
    return db.query(NodesDb).count()

def update_memory(
    node_id: str,
    text: str,
) -> None:
    """Update the text of a memory node.
    
    This function updates the text of a memory node.
    
    Args:
        node_id (str): ID of the memory node.
        text (str): New text of the memory node.
    
    Returns:
        None
    
    Example:
        >>> node_id = 'node_123'
        >>> text = 'This is an updated memory.'
        >>> update_memory(node_id, text)
    """
    db: Session = next(get_db())
    
    try:
        db.query(NodesDb).filter(
            NodesDb.id == node_id
        ).update(
            {NodesDb.text: text}
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def n_gram_search(
    n_gram: str,
) -> List[Memory]:
    """Search for memories using an n-gram.
    
    This function searches for memories using an n-gram.
    
    Args:
        n_gram (str): N-gram to search for.
    
    Returns:
        List[Memory]: List of memories that contain the n-gram.
    
    Example:
        >>> n_gram = 'rohan'
        >>> n_gram_search(n_gram)
    """
    db: Session = next(get_db())
    
    memories = (
        db.query(NodesDb)
        .filter(NodesDb.text.ilike(f"%{n_gram}%"))
        .all()
    )
    
    return [
        Memory(
            content=memory.text,
            created_at=memory.created_at
        )
        for memory in memories
    ]
