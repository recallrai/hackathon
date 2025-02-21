from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Generic, List, Optional, Tuple, TypeVar
from pydantic import BaseModel
from config import BaseLLMConfig, get_settings

settings = get_settings()

T = TypeVar('T', bound=BaseModel)

# class LLMResponse:
#     def __init__(
#         self, 
#         content: str,
#         input_tokens: int,
#         output_tokens: int,
#         model: str
#     ):
#         self.content = content
#         self.input_tokens = input_tokens
#         self.output_tokens = output_tokens
#         self.model = model

class LLMProvider(ABC, Generic[T]):
    def __init__(self, model_config: BaseLLMConfig) -> None:
        self.model_config = model_config

    @abstractmethod
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0
    ) -> AsyncGenerator[str, None]:
        """Stream chat response"""
        pass
        
    @abstractmethod
    def generate_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_model: type[T],
        temperature: float = 0.0
    ) -> T:
        """Generate structured output"""
        pass

    def get_token_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD per 1M tokens"""
        cost = self.model_config.cost
        return (
            (input_tokens * cost.input + output_tokens * cost.output) 
            / 1_000_000
        ) * settings.DOLLAR_TO_INR
