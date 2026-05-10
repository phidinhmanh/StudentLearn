import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from app.config import get_settings

from app.utils.rate_limiter import rate_limit_retry, gemma_limiter, patch_litellm
from app.utils.quota_relief import get_embedding_engine

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
                # Fallback to a generic list if fixed size list fails
                return pa.list_(pa.float32())
            raise

    lancedb.pydantic._pydantic_type_to_arrow_type = _patched_pydantic_to_arrow
    logging.info("LanceDB Pydantic fix applied")
except Exception:
    pass

# Patch litellm BEFORE importing cognee so all internal LLM calls are rate-limited
patch_litellm()

# ── CRITICAL FIX: text-embedding-004 is fixed 768D — API rejects "dimensions" kwarg ──
_EMBEDDING_MODEL_V2 = "gemini/text-embedding-004"

_orig_init = None

def _patched_litellm_init(self, **kwargs):
    """Strip 'dimensions' from kwargs for V2 model — API rejects it with 422."""
    model = kwargs.get("model", getattr(self, "model", None))
    if model and _EMBEDDING_MODEL_V2 in model:
        kwargs["dimensions"] = None  # V2 uses fixed 768D, API errors on 'dimensions'
        # Also ensure dimensions attr is set to 768 for compatibility
        object.__setattr__(self, "dimensions", 768)
    return _orig_init(self, **kwargs)

try:
    from cognee.infrastructure.databases.vector.embeddings.LiteLLMEmbeddingEngine import (
        LiteLLMEmbeddingEngine,
    )
    _orig_init = LiteLLMEmbeddingEngine.__init__
    LiteLLMEmbeddingEngine.__init__ = _patched_litellm_init
    logging.info(f"V2 embedding fix applied: '{_EMBEDDING_MODEL_V2}' will not pass 'dimensions' kwarg")
except ImportError:
    logging.warning("LiteLLMEmbeddingEngine not available for V2 patch — skipping.")

import cognee
from cognee.api.v1.search import SearchType
from cognee import recall as cognee_recall

logger = logging.getLogger(__name__)
settings = get_settings()

# Global semaphore for Cognee ingestion (max 1 concurrent)
_ingest_semaphore = None

def get_ingest_semaphore():
    global _ingest_semaphore
    if _ingest_semaphore is None:
        import asyncio
        _ingest_semaphore = asyncio.Semaphore(1)
    return _ingest_semaphore


@rate_limit_retry(max_retries=5, initial_backoff=5.0, fallback=False)
async def ingest_document(file_path: str, dataset_name: str = "default"):
    """
    Ingest a document into Cognee using the V2 remember API.
    Uses a semaphore to ensure only one ingestion runs at a time.
    """
    sem = get_ingest_semaphore()
    async with sem:
        # Initialize QuotaReliefEngine for use by other endpoints
        get_embedding_engine()
        logger.info(f"Remembering document in Cognee: {file_path} (dataset: {dataset_name})")
        await cognee.remember(file_path, dataset_name = dataset_name)
        return True

@rate_limit_retry(max_retries=3, initial_backoff=2.0, fallback=None)
async def get_knowledge_graph(query: str = None):
    """
    Retrieve or search the knowledge graph.
    If query is provided, performs a RAG search.
    Otherwise, can be used to visualize or list graph data.
    """
    await gemma_limiter.wait()
    if query:
        logger.info(f"Searching Cognee graph with query: {query}")
        results = await cognee.search(
            query_type = SearchType.RAG_COMPLETION,
            query_text = query
        )
        return results
    else:
        return await cognee.visualize_graph()

@rate_limit_retry(max_retries=3, initial_backoff=2.0, fallback="Search unavailable due to quota or error")
async def search_graph(query: str, search_type: SearchType = SearchType.RAG_COMPLETION):
    """
    Search the graph using Cognee.
    """
    await gemma_limiter.wait()
    results = await cognee.search(
        query_type = search_type,
        query_text = query
    )
    return results

@rate_limit_retry(max_retries=3, initial_backoff=2.0, fallback=[])
async def recall_context(query: str, datasets: List[str] = None):
    """
    Use Cognee's V2 recall API to find context.
    """
    await gemma_limiter.wait()
    logger.info(f"Recalling context for query: {query}")
    results = await cognee_recall(
        query_text = query,
        datasets = datasets
    )
    return results
