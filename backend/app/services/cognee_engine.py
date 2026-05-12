import os
import asyncio
import logging
from typing import List

from app.utils.rate_limiter import rate_limit_retry, gemma_limiter, patch_litellm
from app.utils.quota_relief import get_embedding_engine
from app.config import get_settings

settings = get_settings()

# Sync env for Cognee BEFORE importing it
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["LLM_MODEL"] = f"gemini/{settings.gemini_model}"
os.environ["LLM_API_KEY"] = settings.gemini_api_key

# Embedding config for Cognee
os.environ["EMBEDDING_PROVIDER"] = "gemini"
os.environ["EMBEDDING_MODEL"] = "gemini/gemini-embedding-001"
os.environ["EMBEDDING_API_KEY"] = settings.gemini_api_key

# ── CRITICAL FIX: LanceDB/Pydantic TypeError Fix ──
try:
    import lancedb.pydantic
    _orig_pydantic_to_arrow = lancedb.pydantic._pydantic_type_to_arrow_type

    def _patched_pydantic_to_arrow(tp, field):
        try:
            return _orig_pydantic_to_arrow(tp, field)
        except TypeError as e:
            if "an integer is required" in str(e):
                import pyarrow as pa
                return pa.list_(pa.float32())
            raise

    lancedb.pydantic._pydantic_type_to_arrow_type = _patched_pydantic_to_arrow
    logging.info("LanceDB Pydantic fix applied")
except Exception:
    pass

# Patch litellm BEFORE importing cognee
patch_litellm()

# ── CRITICAL FIX: text-embedding-004 fixed 768D ──
_EMBEDDING_MODEL_V2 = "gemini/text-embedding-004"

_orig_init = None

def _patched_litellm_init(self, **kwargs):
    """Strip 'dimensions' kwarg for V2 model."""
    model = kwargs.get("model", getattr(self, "model", None))
    if model and _EMBEDDING_MODEL_V2 in model:
        kwargs["dimensions"] = None
        object.__setattr__(self, "dimensions", 768)
    return _orig_init(self, **kwargs)

try:
    from cognee.infrastructure.databases.vector.embeddings.LiteLLMEmbeddingEngine import (
        LiteLLMEmbeddingEngine,
    )
    _orig_init = LiteLLMEmbeddingEngine.__init__
    LiteLLMEmbeddingEngine.__init__ = _patched_litellm_init
    logging.info(f"V2 embedding fix applied: '{_EMBEDDING_MODEL_V2}'")
except ImportError:
    logging.warning("LiteLLMEmbeddingEngine not available for V2 patch")

import cognee
from cognee.api.v1.search import SearchType

logger = logging.getLogger(__name__)

# Global semaphore for concurrent ingestion
_ingest_semaphore = None

def get_ingest_semaphore():
    global _ingest_semaphore
    if _ingest_semaphore is None:
        _ingest_semaphore = asyncio.Semaphore(1)
    return _ingest_semaphore


@rate_limit_retry(max_retries=5, initial_backoff=5.0, fallback=False)
async def ingest_document(file_path: str, dataset_name: str = "default"):
    """Ingest document into Cognee using V2 API."""
    sem = get_ingest_semaphore()
    async with sem:
        get_embedding_engine()
        logger.info(f"Remembering document: {file_path} (dataset: {dataset_name})")
        await cognee.remember(file_path, dataset_name=dataset_name)
        return True


@rate_limit_retry(max_retries=3, initial_backoff=2.0, fallback=None)
async def get_knowledge_graph(query: str = None):
    """Retrieve or search knowledge graph."""
    await gemma_limiter.wait()
    if query:
        logger.info(f"Searching Cognee graph: {query}")
        results = await cognee.search(
            query_type=SearchType.RAG_COMPLETION,
            query_text=query
        )
        return results
    return await cognee.visualize_graph()


@rate_limit_retry(max_retries=3, initial_backoff=2.0, fallback="Search unavailable")
async def search_graph(query: str, search_type: SearchType = SearchType.RAG_COMPLETION):
    """Search graph using Cognee."""
    await gemma_limiter.wait()
    results = await cognee.search(
        query_type=search_type,
        query_text=query
    )
    return results


@rate_limit_retry(max_retries=3, initial_backoff=2.0, fallback=[])
async def recall_context(query: str, datasets: List[str] = None):
    """Use Cognee recall API."""
    await gemma_limiter.wait()
    logger.info(f"Recalling context: {query}")
    from cognee import recall as cognee_recall
    return await cognee_recall(query_text=query, datasets=datasets)
