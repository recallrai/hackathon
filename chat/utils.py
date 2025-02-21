import re
from typing import TypeVar, Tuple, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

async def process_thinking_response(response_text: str, model_type: Type[T]) -> Tuple[str, T]:
    """
    Extract thinking and JSON response from model output and validate against provided Pydantic model
    
    Args:
        response_text: Raw response text containing thinking and JSON sections
        model_type: Pydantic model class to validate JSON against
    
    Returns:
        Tuple of (thinking_text, validated_model_instance)
    """
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if not json_match:
        raise ValueError("No valid JSON found in response")
    
    thinking_match = re.search(r'<think>(.*?)</think>', response_text, re.DOTALL)
    if not thinking_match:
        raise ValueError("No valid thinking found in response")
        
    return thinking_match.group(1).strip(), model_type.model_validate_json(json_match.group(1))
