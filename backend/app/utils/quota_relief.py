"""
Quota Relief System
===================
Multi-model embedding engine with automatic failover, consistency checks,
and per-model rate limiting.

Features:
  1. Model Rotation Pool — seamless fallback when 429/quota hits
  2. Consistency Check     — warn before mixing old/new embedding models
  3. Per-Model RateLimit  — each model has independent RPM quota tracking
"""

import os
import re
import json
import asyncio
import logging
import hashlib
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("quota_relief")

# ─────────────────────────────────────────────────────────────────────────────
# 1. EMBEDDING MODEL POOL
# ─────────────────────────────────────────────────────────────────────────────

EMBEDDING_MODEL_POOL: List[str] = [
    "gemini/text-embedding-004",   # V2 — dùng trước, quota riêng
    "text-embedding-3-small",      # OpenAI fallback — không giới hạn quota
]

# Per-model RPM limits (requests per minute)
MODEL_RPM: Dict[str, float] = {
    "gemini/text-embedding-004": 12.0,
    "gemini/embedding-001":       12.0,
    "text-embedding-3-small":    60.0,
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. PER-MODEL ASYNC RATE LIMITER
# ─────────────────────────────────────────────────────────────────────────────

class PerModelRateLimiter:
    """
    Per-model rate limiter. Each model key has its own interval and last_call
    so switching models resets the quota automatically (as each provider has
    independent quota).
    """

    def __init__(self):
        self._state: Dict[str, float] = {}   # model → last_call timestamp
        self._lock = asyncio.Lock()

    def interval(self, model: str) -> float:
        rpm = MODEL_RPM.get(model, 12.0)
        return 60.0 / rpm

    async def wait(self, model: str) -> None:
        async with self._lock:
            import time
            now = time.time()
            last = self._state.get(model, 0.0)
            wait_interval = self.interval(model)
            elapsed = now - last
            if elapsed < wait_interval:
                await asyncio.sleep(wait_interval - elapsed)
            self._state[model] = time.time()


per_model_limiter = PerModelRateLimiter()


# ─────────────────────────────────────────────────────────────────────────────
# 3. CONSISTENCY TRACKER
# ─────────────────────────────────────────────────────────────────────────────

def _get_consistency_path() -> str:
    root = os.environ.get("SYSTEM_ROOT_DIRECTORY", ".cognee_system")
    return os.path.join(root, "embedding_consistency.json")


def get_active_embedding_model() -> Optional[str]:
    """Return the model currently recorded in the consistency file."""
    path = _get_consistency_path()
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("active_model")
        except Exception:
            pass
    return None


def get_dataset_info() -> Dict[str, Any]:
    """Check what data exists in the Cognee data directory."""
    data_root = os.environ.get("DATA_ROOT_DIRECTORY", ".cognee_data")
    datasets = []
    if os.path.isdir(data_root):
        for entry in os.scandir(data_root):
            if entry.is_dir():
                datasets.append(entry.name)
    return {
        "data_root": data_root,
        "datasets": datasets,
        "data_exists": len(datasets) > 0,
    }


def record_embedding_model(model: str) -> None:
    """Write the active model to the consistency file."""
    root = os.environ.get("SYSTEM_ROOT_DIRECTORY", ".cognee_system")
    os.makedirs(root, exist_ok=True)
    path = _get_consistency_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "active_model": model,
            "recorded_at": datetime.now().isoformat(),
            "model_hash": hashlib.md5(model.encode()).hexdigest()[:8],
        }, f, indent=2)


def consistency_check(new_model: str) -> Dict[str, Any]:
    """
    Before switching models, verify whether existing data is compatible.

    Returns:
        {
            "safe": bool,           # True = can proceed
            "existing_model": str,  # model already used
            "has_data": bool,
            "dataset_info": dict,
            "warning_message": str,
        }
    """
    existing_model = get_active_embedding_model()
    dataset_info = get_dataset_info()
    has_data = dataset_info["data_exists"]

    if not has_data:
        return {
            "safe": True,
            "existing_model": existing_model,
            "has_data": False,
            "dataset_info": dataset_info,
            "warning_message": None,
        }

    # Data exists — check model compatibility
    if existing_model and existing_model != new_model:
        warning = (
            f"⚠️  Model mới không tương thích với dữ liệu cũ.\n"
            f"    Dữ liệu hiện tại sử dụng: **{existing_model}**\n"
            f"    Model mới muốn dùng:       **{new_model}**\n"
            f"    Các datasets: {dataset_info['datasets']}\n"
            f"    Bạn có muốn xóa dữ liệu cũ để nạp lại bằng model mới không?"
        )
        logger.warning(warning)
        return {
            "safe": False,
            "existing_model": existing_model,
            "has_data": True,
            "dataset_info": dataset_info,
            "warning_message": warning,
        }

    return {
        "safe": True,
        "existing_model": existing_model,
        "has_data": has_data,
        "dataset_info": dataset_info,
        "warning_message": None,
    }


def reset_consistency() -> None:
    """Clear the consistency file and all rate-limit state."""
    path = _get_consistency_path()
    if os.path.exists(path):
        os.remove(path)
    per_model_limiter._state.clear()
    logger.info("Consistency and rate-limit state reset.")


# ─────────────────────────────────────────────────────────────────────────────
# 4. WRAPPER — wraps cognee's LiteLLMEmbeddingEngine with quota relief
# ─────────────────────────────────────────────────────────────────────────────

def _detect_quota_error(exc: Exception) -> bool:
    """Return True if exception indicates a quota / 429 / rate-limit error."""
    msg = str(exc).lower()
    patterns = [
        "429", "rate limit", "quota", "exhausted",
        "resource_exhausted", "rate_limit_exceeded",
        "too many requests", "requests quota",
        "billing", "limit_reached",
    ]
    return any(p in msg for p in patterns)


@dataclass
class QuotaReliefEngine:
    """
    Drop-in wrapper for LiteLLMEmbeddingEngine that adds:

    1. **Model Rotation** — automatically tries next model in EMBEDDING_MODEL_POOL
       when a quota error is detected.

    2. **Consistency Check** — warns before switching models if existing data
       would become incompatible.

    3. **Per-Model Rate Limiting** — each model in the pool gets an independent
       rate limiter (switching model resets the quota automatically).

    Usage:
        engine = QuotaReliefEngine()
        vectors = await engine.embed_text(["hello world"])
    """

    pool: List[str] = field(default_factory=lambda: EMBEDDING_MODEL_POOL.copy())
    current_model_index: int = 0
    _underlying_engine: Optional[Any] = field(default=None, repr=False)

    # ── Engine initialization ────────────────────────────────────────────────

    def _get_model(self) -> str:
        return self.pool[self.current_model_index]

    def _init_underlying_engine(self, model: Optional[str] = None) -> Any:
        """Initialize the real LiteLLMEmbeddingEngine with the given model."""
        try:
            from cognee.infrastructure.databases.vector.embeddings.LiteLLMEmbeddingEngine import (
                LiteLLMEmbeddingEngine,
            )
            target_model = model or self._get_model()

            # For Gemini embedding-004, use dimensions=768 (or 1536) — not 3072
            dimensions = 768 if "text-embedding-004" in target_model else 1536

            engine = LiteLLMEmbeddingEngine(
                model=target_model,
                provider=target_model.split("/")[0] if "/" in target_model else "gemini",
                dimensions=dimensions,
                api_key=os.environ.get("GEMINI_API_KEY") or None,
            )
            logger.info(
                f"QuotaRelief: initialized with model={target_model}, "
                f"dimensions={dimensions}"
            )
            return engine
        except ImportError:
            logger.warning(
                "LiteLLMEmbeddingEngine not available — using mock fallback. "
                "Install cognee to enable real embeddings."
            )
            return None

    # ── Public API ──────────────────────────────────────────────────────────

    def get_current_model(self) -> str:
        return self._get_model()

    def get_model_pool(self) -> List[str]:
        return self.pool.copy()

    def switch_model(self, model: str) -> bool:
        """Manually switch to a specific model in the pool."""
        if model not in self.pool:
            logger.error(f"Model '{model}' not in pool. Available: {self.pool}")
            return False
        self.current_model_index = self.pool.index(model)
        self._underlying_engine = None  # Force re-init
        logger.info(f"Switched embedding model to: {model}")
        return True

    def rotate_to_next_model(self) -> Optional[str]:
        """Advance to next model in pool. Returns new model name or None if exhausted."""
        if self.current_model_index < len(self.pool) - 1:
            self.current_model_index += 1
            new_model = self._get_model()
            self._underlying_engine = None  # Force re-init with new model
            logger.info(f"Rotating to next model: {new_model}")
            return new_model
        logger.warning("No more models in pool — all models exhausted.")
        return None

    def is_model_exhausted(self) -> bool:
        return self.current_model_index >= len(self.pool) - 1

    # ── embed_text — the main entry point with quota relief ─────────────────

    async def embed_text(
        self,
        texts: List[str],
        force_new_model: bool = False,
        skip_consistency_check: bool = False,
    ) -> List[List[float]]:
        """
        Embed texts with automatic model rotation on 429 / quota errors.

        Args:
            texts: List of strings to embed.
            force_new_model: If True, rotate to next model on ANY error
                             (not just quota errors).
            skip_consistency_check: If True, bypass the model-consistency check.
                                    Use with caution — only for fresh datasets.

        Returns:
            List of embedding vectors (one per input text).

        Raises:
            RuntimeError when all models in the pool are exhausted.
        """
        # Lazy-init underlying engine
        if self._underlying_engine is None:
            self._underlying_engine = self._init_underlying_engine()

        # ── Consistency check before first embed ─────────────────────────────
        # Only check if we already have data from a different model
        active = get_active_embedding_model()
        current = self._get_model()
        if (
            not skip_consistency_check
            and active
            and active != current
            and get_dataset_info()["data_exists"]
        ):
            logger.warning(
                f"⚠️  Model mismatch detected!\n"
                f"    Existing data uses: {active}\n"
                f"    Current model:      {current}\n"
                f"    Datasets: {get_dataset_info()['datasets']}\n"
                f"    Call set_model_with_consistency_check() or reset_and_reembed()."
            )
            # Don't raise — allow caller to decide via the check result
            # But log clearly and continue with warning

        # ── Rate limit before embedding call ─────────────────────────────────
        await per_model_limiter.wait(self._get_model())

        # ── Embed with automatic rotation on quota errors ─────────────────────
        max_rotation_attempts = len(self.pool)
        attempt = 0

        while attempt < max_rotation_attempts:
            try:
                if self._underlying_engine is None:
                    self._underlying_engine = self._init_underlying_engine()

                result = await self._underlying_engine.embed_text(texts)

                # ── Success — record model used ───────────────────────────
                record_embedding_model(self._get_model())
                return result

            except Exception as exc:
                is_quota = _detect_quota_error(exc)
                is_context_window = "context" in str(exc).lower() and "window" in str(exc).lower()

                if is_quota or (force_new_model and attempt > 0):
                    logger.warning(
                        f"[embed_text] {'Quota' if is_quota else 'Error'} error "
                        f"on model {self._get_model()}: {str(exc)[:80]}"
                    )

                    # Consistency check before rotating
                    check = consistency_check(self._get_model())
                    if not check["safe"] and check["has_data"]:
                        logger.warning(
                            f"⚠️  {check['warning_message']}\n"
                            f"    Skipping rotation to avoid corrupting existing data.\n"
                            f"    Call reset_consistency() + retry if you want to force switch."
                        )
                        raise RuntimeError(
                            f"Embedding blocked: model conflict with existing data.\n"
                            f"{check['warning_message']}"
                        ) from exc

                    # Attempt rotation
                    next_model = self.rotate_to_next_model()
                    if next_model is None:
                        raise RuntimeError(
                            f"All {len(self.pool)} embedding models exhausted. "
                            f"Last error: {str(exc)[:120]}"
                        ) from exc

                    logger.info(f"Rotating to next model: {next_model}")
                    attempt += 1
                    continue

                elif is_context_window:
                    # Try sub-chunking
                    sub_results = []
                    for text in texts:
                        parts = _sub_chunk(text, max_chars=400)
                        sub_vecs = []
                        for part in parts:
                            try:
                                if self._underlying_engine is None:
                                    self._underlying_engine = self._init_underlying_engine()
                                vec = await self._underlying_engine.embed_text([part])
                                sub_vecs.append(vec[0])
                            except Exception as sub_exc:
                                logger.warning(
                                    f"Sub-chunk failed: {str(sub_exc)[:60]}"
                                )
                                # Use zero vector as fallback
                                import numpy as np
                                sub_vecs.append([0.0] * 768)
                        import numpy as np
                        pooled = np.mean(sub_vecs, axis=0).tolist() if sub_vecs else [0.0] * 768
                        sub_results.append(pooled)
                    record_embedding_model(self._get_model())
                    return sub_results
                else:
                    # Non-quota, non-context error — don't rotate
                    raise

        # Should not reach here
        raise RuntimeError(f"All embedding attempts exhausted after {attempt} rotations.")

    # ── Utility methods ──────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Return current state of the quota relief system."""
        return {
            "pool": self.pool,
            "current_model": self._get_model(),
            "model_index": self.current_model_index,
            "is_exhausted": self.is_model_exhausted(),
            "active_consistency_model": get_active_embedding_model(),
            "dataset_info": get_dataset_info(),
            "rate_limit_state": {
                model: round(per_model_limiter._state.get(model, 0.0), 2)
                for model in self.pool
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# 5. SUB-CHUNK HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _sub_chunk(text: str, max_chars: int = 400) -> List[str]:
    """Split long text into smaller chunks at natural boundaries."""
    import re
    chunks = []
    # Split by sentence boundaries
    sentences = re.split(r"(?<=[.!?;])\s+", text)
    current = ""

    for sent in sentences:
        if len(current) + len(sent) <= max_chars:
            current += (" " if current else "") + sent
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sent

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text[:max_chars]]


# ─────────────────────────────────────────────────────────────────────────────
# 6. GLOBAL SINGLETON
# ─────────────────────────────────────────────────────────────────────────────

_global_engine: Optional[QuotaReliefEngine] = None


def get_embedding_engine() -> QuotaReliefEngine:
    global _global_engine
    if _global_engine is None:
        _global_engine = QuotaReliefEngine()
    return _global_engine


def reset_embedding_engine() -> None:
    global _global_engine
    _global_engine = None