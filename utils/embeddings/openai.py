import openai
from openai.types import CreateEmbeddingResponse
from typing import Any, Dict, List, Union
from .base import EmbeddingsProvider
from config import BaseLLMConfig

class OpenAIProvider(EmbeddingsProvider):
    def __init__(self, model_config: BaseLLMConfig):
        super().__init__(model_config)
        self.client = openai.OpenAI(
            api_key=model_config.api_key,
        )

    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        # dimensions: int = None
    ) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        
        response: CreateEmbeddingResponse = self.client.embeddings.create(
            input=texts,
            model=self.model_config.name,
            # dimensions=dimensions
        )
        return [embedding.embedding for embedding in response.data]

if __name__ == '__main__':
    from config import get_settings
    config = get_settings()
    provider = OpenAIProvider(config.embedding_model)
    provider.get_embeddings('Hello, world!')
