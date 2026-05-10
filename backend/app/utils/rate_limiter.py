import asyncio
import logging
import functools
from typing import Any, Callable, TypeVar
import time

logger = logging.getLogger(__name__)

T = TypeVar("T")

class AsyncRateLimiter:
    """Enforces a maximum number of requests per minute (RPM)."""
    def __init__(self, rpm: int):
        self.interval = 60.0 / rpm
        self.last_call = 0.0
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            if elapsed < self.interval:
                wait_time = self.interval - elapsed
                await asyncio.sleep(wait_time)
            self.last_call = time.time()

# Global limiter for LLM calls (12 RPM with 3 safety margin from 15)
gemma_limiter = AsyncRateLimiter(rpm=12)

# Global limiter for Embedding calls (80 RPM, leaving headroom from 100 limit)
embedding_limiter = AsyncRateLimiter(rpm=80)


def patch_litellm():
    """Monkey-patch litellm to respect our global rate limiters."""
    try:
        import litellm

        # Patch async completion (LLM calls)
        original_acompletion = getattr(litellm, "acompletion", None)
        if original_acompletion and not getattr(original_acompletion, "_is_patched", False):
            async def patched_acompletion(*args, **kwargs):
                await gemma_limiter.wait()
                return await original_acompletion(*args, **kwargs)
            patched_acompletion._is_patched = True
            litellm.acompletion = patched_acompletion
            logger.info("Patched litellm.acompletion")

        # Patch sync completion
        original_completion = getattr(litellm, "completion", None)
        if original_completion and not getattr(original_completion, "_is_patched", False):
            def patched_completion(*args, **kwargs):
                return original_completion(*args, **kwargs)
            patched_completion._is_patched = True
            litellm.completion = patched_completion
            logger.info("Patched litellm.completion")

        # Patch async embedding (ALSO rate-limited to avoid 429 on embedding quota)
        original_aembedding = getattr(litellm, "aembedding", None)
        if original_aembedding and not getattr(original_aembedding, "_is_patched", False):
            async def patched_aembedding(*args, **kwargs):
                await embedding_limiter.wait()
                return await original_aembedding(*args, **kwargs)
            patched_aembedding._is_patched = True
            litellm.aembedding = patched_aembedding
            logger.info("Patched litellm.aembedding")

        # Patch sync embedding
        original_embedding = getattr(litellm, "embedding", None)
        if original_embedding and not getattr(original_embedding, "_is_patched", False):
            def patched_embedding(*args, **kwargs):
                return original_embedding(*args, **kwargs)
            patched_embedding._is_patched = True
            litellm.embedding = patched_embedding
            logger.info("Patched litellm.embedding")

    except Exception as e:
        logger.warning(f"Could not patch litellm: {e}")

# Run initial patch
patch_litellm()


def rate_limit_retry(max_retries: int = 5, initial_backoff: float = 2.0, fallback: Any = None):
    """
    Decorator to retry a function with exponential backoff when hitting 429 (Rate Limit).
    If max retries hit, returns the fallback value instead of raising.
    """
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            backoff = initial_backoff

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    err_msg = str(e).lower()

                    # Check for 429, Rate Limit, Quota exceeded, or Resource Exhausted
                    if any(term in err_msg for term in ["429", "rate limit", "quota", "exhausted", "resource_exhausted"]):
                        wait_time = backoff * (2 ** attempt)
                        logger.warning(
                            f"Quota hit ({func.__name__}). Retrying in {wait_time:.1f}s (Attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        # For other exceptions, log briefly and return fallback or raise
                        logger.warning(f"Error in {func.__name__}: {str(e)[:100]}")
                        if fallback is not None:
                            return fallback
                        raise

            logger.warning(f"Failed {func.__name__} after {max_retries} attempts. Returning fallback.")
            return fallback

        return wrapper
    return decorator
