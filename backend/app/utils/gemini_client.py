from threading import Lock

from langchain_openai import ChatOpenAI

from app.config import get_settings

_provider_lock = Lock()
_provider_index = 0


def _parse_provider_order(raw_order: str) -> list[str]:
    providers = [provider.strip() for provider in raw_order.split(",") if provider.strip()]
    return providers or ["nvidia"]


def _next_provider_order(raw_order: str) -> list[str]:
    global _provider_index

    providers = _parse_provider_order(raw_order)
    with _provider_lock:
        start = _provider_index % len(providers)
        _provider_index = (_provider_index + 1) % len(providers)

    return providers[start:] + providers[:start]


def get_llm(temperature: float = 0) -> ChatOpenAI:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required for LLM requests")

    provider_order = _next_provider_order(settings.openrouter_provider_order)
    return ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=temperature,
        timeout=120,
        extra_body={
            "provider": {
                "order": provider_order,
                "allow_fallbacks": True,
            }
        },
    )