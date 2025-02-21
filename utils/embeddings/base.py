from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

class EmbeddingsProvider(ABC):
    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config

    @abstractmethod
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        # dimensions: int = None
    ) -> List[List[float]]:
        """Generate embeddings for input texts"""
        pass

    def get_token_cost(self, num_tokens: int) -> float:
        """Calculate cost in USD per 1M tokens"""
        cost = self.model_config['cost']
        return (num_tokens * cost['input']) / 1_000_000
