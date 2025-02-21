from pydantic import BaseModel, field_validator
from typing import List, Dict, Union
from enum import Enum

##* CLASSIFIER
class ClassifierOutput(BaseModel):
    memory_usage: bool

##* QUERY KEYWORDS GENERATOR
class QueryKeywordsGeneratorOutputType(Enum):
    # FUNCTION_CALL = "function_call"
    FINAL_RESULT = "final_result"

class QueryKeywordsGeneratorResponse(BaseModel):
    bm25_keywords: List[str]
    vector_search_queries: List[str]

class QueryKeywordsGeneratorFunctionCall(BaseModel):
    name: str
    arguments: Dict

class QueryKeywordsGeneratorOutput(BaseModel):
    type: QueryKeywordsGeneratorOutputType
    data: Union[QueryKeywordsGeneratorFunctionCall, QueryKeywordsGeneratorResponse]

##* MEMORY GENERATION
class GenerationOutputType(Enum):
    FUNCTION_CALL = "function_call"
    FINAL_RESULT = "final_result"

class MemoryResponse(BaseModel):
    memories: List[str]

class FunctionCall(BaseModel):
    name: str
    arguments: Dict

class ModelResponseGeneration(BaseModel):
    type: GenerationOutputType
    data: Union[FunctionCall, MemoryResponse]

##* DECISION

class DecisionOutputType(Enum):
    INSERT = "INSERT"
    MERGE_CONFLICT = "MERGE_CONFLICT"
    RESOLVE_TEMPORAL_CONFLICT = "RESOLVE_TEMPORAL_CONFLICT"
    ADDITION_TO_EXISTING_MEMORY = "ADDITION_TO_EXISTING_MEMORY"
    IGNORE = "IGNORE"

class InsertAction(BaseModel):
    content: str

class ConflictingMemory(BaseModel):
    memory_id: str
    content: str
    reason: str

class MergeConflictAction(BaseModel):
    conflicting_memories: List[ConflictingMemory]

class ResolveTemporalConflictAction(BaseModel):
    memory_ids: List[int]

class UpdatedMemory(BaseModel):
    memory_id: str
    content: str

class AdditionToExistingMemoryAction(BaseModel):
    updated_memories: List[UpdatedMemory]

class IgnoreAction(BaseModel):
    reason: str

class ModelResponseDecision(BaseModel):
    action: DecisionOutputType
    data: Union[
        InsertAction, MergeConflictAction, ResolveTemporalConflictAction, 
        AdditionToExistingMemoryAction, IgnoreAction
    ]

    @field_validator('data')
    def validate_data_type(cls, v, info):
        action = info.data.get('action')
        if action == DecisionOutputType.INSERT and not isinstance(v, InsertAction):
            raise ValueError('data must be InsertAction when action is INSERT')
        elif action == DecisionOutputType.MERGE_CONFLICT and not isinstance(v, MergeConflictAction):
            raise ValueError('data must be MergeConflictAction when action is MERGE_CONFLICT')
        elif action == DecisionOutputType.RESOLVE_TEMPORAL_CONFLICT and not isinstance(v, ResolveTemporalConflictAction):
            raise ValueError('data must be ResolveTemporalConflictAction when action is RESOLVE_TEMPORAL_CONFLICT')
        elif action == DecisionOutputType.ADDITION_TO_EXISTING_MEMORY and not isinstance(v, AdditionToExistingMemoryAction):
            raise ValueError('data must be AdditionToExistingMemoryAction when action is ADDITION_TO_EXISTING_MEMORY')
        elif action == DecisionOutputType.IGNORE and not isinstance(v, IgnoreAction):
            raise ValueError('data must be IgnoreAction when action is IGNORE')
        return v

##* INSERTION PROMPT
class ModelResponseInsertion(BaseModel):
    related_memory_ids: List[Union[str, int]]

    @field_validator('related_memory_ids')
    def convert_ids_to_int(cls, v):
        return [str(id) for id in v]

##* ADDITION PROMPT
class ModelResponseAddition(BaseModel):
    related_memory_ids: List[Union[str, int]]

    @field_validator('related_memory_ids')
    def convert_ids_to_str(cls, v):
        return [str(id) for id in v]
