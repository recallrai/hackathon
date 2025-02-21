from typing import Dict, Any
from .base import EmbeddingsProvider
from .openai import OpenAIProvider
from config import EmbeddingConfig

class EmbeddingsFactory:
    @staticmethod 
    def create_provider(model_config: EmbeddingConfig) -> EmbeddingsProvider:
        provider = model_config.provider.lower()
        if provider == 'openai':
            return OpenAIProvider(model_config)
        else:
            raise ValueError(f"Unknown embeddings provider: {provider}")
