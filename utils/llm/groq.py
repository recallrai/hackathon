import instructor
from groq import Groq
from typing import Any, AsyncGenerator, Dict, List
from .base import LLMProvider, T
from config import BaseLLMConfig

class GroqProvider(LLMProvider[T]):
    def __init__(self, model_config: BaseLLMConfig) -> None:
        super().__init__(model_config)
        self.raw_client = Groq(api_key=model_config.api_key)
        self.structured_client = instructor.from_groq(
            self.raw_client,
            mode=instructor.Mode.JSON
        )

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0
    ) -> AsyncGenerator[str, None]:
        stream = self.raw_client.chat.completions.create(
            model=self.model_config.name,
            messages=messages,
            temperature=temperature,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def generate_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_model: type[T],
        temperature: float = 0.0
    ) -> T:
        response = self.structured_client.chat.completions.create(
            model=self.model_config.name,
            messages=messages,
            response_model=response_model,
            temperature=temperature
        )
        return response
