import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gemini / OpenRouter-compatible LLM
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-oss-120b"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_provider_order: str = "nvidia,groq,together"
    
    # GraphRAG Models
    graphrag_qa_model: str = "models/gemini-2.0-flash"
    graphrag_cypher_model: str = "models/gemini-2.0-flash"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

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


@lru_cache()
def get_settings() -> Settings:
    return Settings()