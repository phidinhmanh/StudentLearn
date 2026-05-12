import os
from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache


class Settings(BaseSettings):
    # Core LLM settings (Single source of truth)
    gemini_api_key: str = ""
    gemini_model: str = "gemma-4-26b-a4b-it"
    gemini_fallback_model: str = "gemma-4-31b-it"

    # Fallback / Alternative Providers
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-4-26b-a4b-it"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_provider_order: str = "google,groq,together"

    # Derived LLM & Embedding Settings (Cognee compatibility)
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    llm_model: str = ""
    embedding_provider: str = "gemini"
    embedding_model: str = "gemini/text-embedding-004"
    embedding_api_key: str = ""

    # Derived GraphRAG Models
    graphrag_qa_model: str = ""
    graphrag_cypher_model: str = ""

    # Graph Storage & Provider
    graph_database_provider: str = "kuzu"
    graph_provider: str = "cognee"
    cognee_api_key: str = ""
    system_root_directory: str = ".cognee_system"
    data_root_directory: str = ".cognee_data"

    # Security & Auth
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # System
    max_file_size_mb: int = 100

    @model_validator(mode='after')
    def sync_derived_configs(self):
        # Populate generic env vars for Cognee's LLM client.
        os.environ["LLM_PROVIDER"] = "gemini"
        os.environ["LLM_MODEL"] = f"gemini/{self.gemini_model}"
        os.environ["LLM_API_KEY"] = self.gemini_api_key

        # ── CRITICAL: Set Embedding env vars for Cognee v1.0.3 ──
        os.environ["EMBEDDING_PROVIDER"] = "gemini"
        os.environ["EMBEDDING_MODEL"] = "gemini/gemini-embedding-001"
        os.environ["EMBEDDING_API_KEY"] = self.gemini_api_key
        if not self.graphrag_qa_model:
            self.graphrag_qa_model = self.gemini_model
        if not self.graphrag_cypher_model:
            self.graphrag_cypher_model = self.gemini_model

        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()