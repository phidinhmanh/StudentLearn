import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gemini / OpenRouter-compatible LLM
    gemini_api_key: str = ""
    gemini_model: str = "gemma-4-26b-a4b-it"
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-4-26b-a4b-it"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_provider_order: str = "nvidia,groq,together"
    nvidia_api_key: str = ""
    nvidia_model: str = "meta/llama-3.1-70b-instruct"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"

    # GraphRAG Models
    graphrag_qa_model: str = "gemma-4-26b-a4b-it"

    # Graph Database Provider (kuzu, networkx, etc. for Cognee)
    graph_database_provider: str = "kuzu"

    # Graph Provider (cognee)
    graph_provider: str = "cognee"
    cognee_api_key: str = ""
    system_root_directory: str = ".cognee_system"
    data_root_directory: str = ".cognee_data"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # File upload
    max_file_size_mb: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()