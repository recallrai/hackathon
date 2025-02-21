import json
from typing import List, Union
from pydantic_settings import BaseSettings
from pathlib import Path
from pydantic import BaseModel, field_validator
from functools import lru_cache
from enum import Enum

# class ModelType(str, Enum):
#     LLM = 'llms'
#     EMBEDDING = 'embeddings'

class LLMCost(BaseModel):
    input: float
    output: float

class EmbeddingCost(BaseModel):
    input: float

class BaseLLMConfig(BaseModel):
    provider: str
    name: str
    api_key: str
    cost: LLMCost

class EmbeddingConfig(BaseModel):
    provider: str
    name: str
    n_dim: int
    api_key: str
    cost: EmbeddingCost

class ModelsConfig(BaseModel):
    llms: List[BaseLLMConfig]
    embedding: EmbeddingConfig

class Settings(BaseSettings):
    # Environment Configuration
    ENV: str = 'development'

    # Auth Configuration
    AUTH_USERNAME: Union[str, None] = None
    AUTH_PASSWORD: Union[str, None] = None

    @field_validator('AUTH_USERNAME')
    def validate_auth_username(cls, v, values):
        if values.data.get('ENV') == 'production' and not v:
            raise ValueError("AUTH_USERNAME must be set in production")
        return v

    @field_validator('AUTH_PASSWORD')
    def validate_auth_password(cls, v, values):
        if values.data.get('ENV') == 'production' and not v:
            raise ValueError("AUTH_PASSWORD must be set in production")
        return v

    # PostgreSQL Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    # MongoDB Configuration
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_DB: str
    MONGO_COLLECTION: str

    # Milvus Configuration
    # MILVUS_USER: str
    # MILVUS_PASSWORD: str
    MILVUS_HOST: str
    MILVUS_PORT: str
    MILVUS_COLLECTION: str

    # LLM Configuration
    MODELS_CONFIG_PATH: str

    # Pricing Configuration
    DOLLAR_TO_INR: float

    @field_validator('MODELS_CONFIG_PATH')
    def check_models_config_path(cls, value):
        if not Path(value).exists():
            raise ValueError(f"Models config file not found at {value}")
        
        ModelsConfig.model_validate(json.load(open(value, 'r')))
        return value

    def get_postgres_uri(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_mongo_uri(self) -> str:
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"

    def get_milvus_uri(self) -> str:
        return f"tcp://{self.MILVUS_HOST}:{self.MILVUS_PORT}"

    @property
    def ModelConfig(self) -> ModelsConfig:
        """Loads and caches the model configuration from the specified JSON file"""
        if not hasattr(self, '_model_config'):
            with open(self.MODELS_CONFIG_PATH, 'r') as f:
                self._model_config = ModelsConfig.model_validate(json.load(f))
        return self._model_config

    @property
    def llms(self) -> List[BaseLLMConfig]:
        return self.ModelConfig.llms

    def get_llm_config(self, model_name: str) -> BaseLLMConfig:
        for model in self.ModelConfig.llms:
            if model.name == model_name:
                return model
        raise ValueError(f"Model {model_name} not found in the configuration")

    @property
    def embedding_model(self) -> EmbeddingConfig:
        return self.ModelConfig.embedding

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
