import openai
from typing import Any, AsyncGenerator, Dict, List
from .base import LLMProvider, T
from config import BaseLLMConfig

class GeminiProvider(LLMProvider[T]):
    def __init__(self, model_config: BaseLLMConfig) -> None:
        super().__init__(model_config)
        self.client = openai.OpenAI(
            api_key=model_config.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        stream = self.client.chat.completions.create(
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
        temperature: float = 0.7
    ) -> T:
        response = self.client.chat.completions.create(
            model=self.model_config.name,
            messages=messages,
            temperature=temperature,
            # TODO: fix this.
            response_format={"type": "json_object"},
            response_model=response_model
        )
        return response.choices[0].message.parsed
