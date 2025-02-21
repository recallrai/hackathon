from pydantic import BaseModel
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
