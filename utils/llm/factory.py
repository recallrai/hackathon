from typing import Dict, Any
from .base import LLMProvider
from .openai import OpenAIProvider 
from .groq import GroqProvider
from .together_ai import TogetherAIProvider
from .sambanova import SambaNovaProvider
from .gemini import GeminiProvider
from config import BaseLLMConfig

class LLMFactory:
    @staticmethod
    def create_provider(model_config: BaseLLMConfig) -> LLMProvider:
        provider = model_config.provider.lower()
        if provider == 'openai':
            return OpenAIProvider(model_config)
        elif provider == 'groq':
            return GroqProvider(model_config)
        elif provider == 'together ai':
            return TogetherAIProvider(model_config)
        elif provider == 'samba nova':
            return SambaNovaProvider(model_config)
        elif provider == 'google':
            return GeminiProvider(model_config)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
