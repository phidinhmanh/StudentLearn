from langchain_openai import ChatOpenAI
from app.config import get_settings

def get_llm(temperature: float = 0) -> ChatOpenAI:
    settings = get_settings()
    api_key = settings.openrouter_api_key or settings.gemini_api_key or "test-key"
    return ChatOpenAI(
        model=settings.openrouter_model,
        api_key=api_key,
        base_url=settings.openrouter_base_url,
        temperature=temperature,
        timeout=10,
    )