# function to convert uuidv4 to normal int so that LLMs can easily make relations
from typing import Dict, List
from utils.models import Memory

# TODO: make pydantic model for this shit
def normalize_memories(memories: List[Memory]):
    """
    Example Memory:
    [
        {
            "id": "uuid",
            "created_at": "datetime",
            "text": "string",
        },
        ...
    ]
    
    Example Output:
    {
        "memories": [
            {
                "id": "int",
                "created_at": "datetime",
                "text": "string",
            },
            ...
        ],
        "uuid_mappping": {
            "uuid": "int",
            ...
        }
    }
    """
    uuid_mapping = {}
    for idx, memory in enumerate(memories):
        memory_id = memory.id
        uuid_mapping[memory_id] = idx
        memory.id = idx

    return memories, uuid_mapping
