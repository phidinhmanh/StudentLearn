import asyncio
import logging
import os
import time
from typing import Any, Dict

from app.config import get_settings
from app.utils.rate_limiter import embedding_limiter, gemma_limiter

# Setup dedicated logger for diagnostics → writes to .cognee_system/debug.log
_diag_logger: logging.Logger | None = None

def _get_diag_logger() -> logging.Logger:
    global _diag_logger
    if _diag_logger is None:
        settings = get_settings()
        log_dir = os.path.abspath(settings.system_root_directory)
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "debug.log")

        _diag_logger = logging.getLogger("app.diagnostics")
        _diag_logger.setLevel(logging.DEBUG)
        _diag_logger.handlers.clear()

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        _diag_logger.addHandler(file_handler)
    return _diag_logger


async def check_db_connection() -> Dict[str, Any]:
    """Verify .cognee_system directory exists and is accessible."""
    try:
        settings = get_settings()
        path = os.path.abspath(settings.system_root_directory)
        if os.path.exists(path) and os.access(path, os.R_OK | os.W_OK):
            test_file = os.path.join(path, ".diag_write_test")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(test_file)
            return {
                "name": "db_connection",
                "status": True,
                "message": "Cognee system directory accessible and writable",
            }
        return {
            "name": "db_connection",
            "status": False,
            "message": f"Directory not accessible: {path}",
        }
    except Exception as e:
        return {"name": "db_connection", "status": False, "message": str(e)[:120]}


async def check_file_permissions() -> Dict[str, Any]:
    """Verify write permissions on data directories."""
    try:
        settings = get_settings()
        test_dir = os.path.join(
            os.path.abspath(settings.data_root_directory), ".diag_test"
        )
        os.makedirs(test_dir, exist_ok=True)
        os.rmdir(test_dir)
        return {"name": "file_permissions", "status": True, "message": "Write permissions OK"}
    except Exception as e:
        return {"name": "file_permissions", "status": False, "message": str(e)[:120]}


async def check_llm_connection() -> Dict[str, Any]:
    """Test LLM connectivity via LiteLLM with a trivial prompt."""
    try:
        import litellm

        start = time.time()
        await gemma_limiter.wait()
        response = await litellm.acompletion(
            model="gemini/gemini-2.0-flash",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        elapsed = time.time() - start
        content = response.choices[0].message.content.strip()
        return {
            "name": "llm_connection",
            "status": True,
            "message": f"LLM responded in {elapsed:.1f}s: {content}",
            "details": {"elapsed_seconds": round(elapsed, 2)},
        }
    except Exception as e:
        return {"name": "llm_connection", "status": False, "message": str(e)[:120]}


async def check_rate_limit_status() -> Dict[str, Any]:
    """Return current state of rate limiters."""
    try:
        return {
            "name": "rate_limit_status",
            "status": True,
            "message": "Rate limiters active",
            "details": {
                "gemma": {
                    "interval_seconds": round(gemma_limiter.interval, 2),
                    "rpm_limit": round(60 / gemma_limiter.interval, 1),
                },
                "embedding": {
                    "interval_seconds": round(embedding_limiter.interval, 2),
                    "rpm_limit": round(60 / embedding_limiter.interval, 1),
                },
            },
        }
    except Exception as e:
        return {"name": "rate_limit_status", "status": False, "message": str(e)[:120]}


async def check_all() -> Dict[str, Any]:
    """Run all diagnostics and return consolidated report."""
    names = ["db_connection", "file_permissions", "llm_connection", "rate_limit_status"]
    checks = await asyncio.gather(
        check_db_connection(),
        check_file_permissions(),
        check_llm_connection(),
        check_rate_limit_status(),
        return_exceptions=True,
    )
    results = []
    for i, check in enumerate(checks):
        if isinstance(check, Exception):
            results.append({"name": names[i], "status": False, "message": str(check)[:120]})
        else:
            results.append(check)

    all_ok = all(r["status"] for r in results)
    return {"overall_status": "ok" if all_ok else "degraded", "checks": results}