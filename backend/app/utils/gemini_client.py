import asyncio
import logging
from threading import Lock
from typing import Any, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.utils.rate_limiter import gemma_limiter

logger = logging.getLogger(__name__)

# Thread-safe round-robin over provider list
_provider_lock = Lock()
_provider_index = 0


def _parse_provider_order(raw_order: str) -> List[str]:
    providers = [p.strip() for p in raw_order.split(",") if p.strip()]
    return providers or ["google", "groq", "together"]


def _next_provider_order(raw_order: str) -> List[str]:
    global _provider_index
    providers = _parse_provider_order(raw_order)
    with _provider_lock:
        start = _provider_index % len(providers)
        _provider_index = (_provider_index + 1) % len(providers)
    return providers[start:] + providers[:start]


def get_llm(temperature: float = 0) -> "LLMWithFallback":
    """Returns a wrapper that handles OpenRouter -> Gemini fallback."""
    return LLMWithFallback(temperature=temperature)


class LLMWithFallback:
    """Wrapper to handle automatic provider fallback on invocation."""

    def __init__(self, temperature: float = 0):
        self.temperature = temperature
        self.settings = get_settings()

    def _get_openrouter(self) -> ChatOpenAI:
        provider_order = _next_provider_order(self.settings.openrouter_provider_order)
        return ChatOpenAI(
            model=self.settings.openrouter_model,
            api_key=self.settings.openrouter_api_key,
            base_url=self.settings.openrouter_base_url,
            temperature=self.temperature,
            timeout=120,
            extra_body={
                "provider": {
                    "order": provider_order,
                    "allow_fallbacks": True,
                }
            },
        )

    def _get_gemini(self, model_name: str | None = None) -> ChatGoogleGenerativeAI:
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set for fallback")
        return ChatGoogleGenerativeAI(
            model=model_name or self.settings.gemini_model,
            api_key=self.settings.gemini_api_key,
            temperature=self.temperature,
        )

    async def ainvoke(self, prompt: str) -> Any:
        """Asynchronous invoke with fallback and rate limiting."""
        # 1. Try OpenRouter
        if self.settings.openrouter_api_key:
            try:
                client = self._get_openrouter()
                return await client.ainvoke(prompt)
            except Exception as e:
                logger.warning("OpenRouter failed (%s), falling back to Gemini", e)

        # 2. Try Gemini
        if self.settings.gemini_api_key:
            try:
                await gemma_limiter.wait() # 15 RPM
                client = self._get_gemini(self.settings.gemini_model)
                return await client.ainvoke(prompt)
            except Exception as e:
                if self.settings.gemini_fallback_model:
                    try:
                        await gemma_limiter.wait() # 15 RPM
                        logger.warning("Gemini primary model failed (%s), trying fallback model: %s", e, self.settings.gemini_fallback_model)
                        client = self._get_gemini(self.settings.gemini_fallback_model)
                        return await client.ainvoke(prompt)
                    except Exception as e2:
                        logger.warning("Gemini fallback model also failed (%s)", e2)
                else:
                    logger.warning("Gemini failed (%s)", e)

        raise RuntimeError("No LLM providers available (check API keys)")

    def invoke(self, prompt: str) -> Any:
        """Synchronous invoke with fallback. Used with asyncio.to_thread."""
        # 1. Try OpenRouter
        if self.settings.openrouter_api_key:
            try:
                client = self._get_openrouter()
                return client.invoke(prompt)
            except Exception as e:
                # Catch 402, 401, 429 or any connection error
                logger.warning("OpenRouter failed (%s), falling back to Gemini", e)

        # 2. Try Gemini
        if self.settings.gemini_api_key:
            try:
                client = self._get_gemini(self.settings.gemini_model)
                return client.invoke(prompt)
            except Exception as e:
                if self.settings.gemini_fallback_model:
                    try:
                        logger.warning("Gemini primary model failed (%s), trying fallback model: %s", e, self.settings.gemini_fallback_model)
                        client = self._get_gemini(self.settings.gemini_fallback_model)
                        return client.invoke(prompt)
                    except Exception as e2:
                        logger.warning("Gemini fallback model also failed (%s)", e2)
                else:
                    logger.warning("Gemini failed (%s)", e)

        raise RuntimeError("No LLM providers available (check API keys)")
