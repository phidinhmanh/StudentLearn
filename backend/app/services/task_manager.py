import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Simple in-memory task manager for demo purposes.
# In production, this would use Redis or a database.
_tasks: Dict[str, Dict[str, Any]] = {}

def create_task(doc_id: str, filename: str) -> str:
    task_id = str(uuid.uuid4())
    _tasks[task_id] = {
        "task_id": task_id,
        "doc_id": doc_id,
        "filename": filename,
        "status": "processing",
        "progress": 0,
        "message": "Starting ingestion...",
        "steps": [],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "error": None
    }
    return task_id

def update_task(task_id: str, **kwargs):
    if task_id in _tasks:
        _tasks[task_id].update(kwargs)
        if kwargs.get("status") in ["completed", "failed"]:
            _tasks[task_id]["completed_at"] = datetime.now().isoformat()

def update_task_progress(task_id: str, progress: int, message: str, step_key: str = None):
    """
    Update task progress with smooth percentage and optional step tracking.
    Args:
        task_id: The task ID to update
        progress: Overall progress percentage (0-100)
        message: Human-readable status message
        step_key: Optional key for sub-step tracking (e.g., "extracting", "embedding")
    """
    if task_id in _tasks:
        _tasks[task_id]["progress"] = progress
        _tasks[task_id]["message"] = message
        _tasks[task_id]["status"] = "processing"

        # Track individual steps for UI log display
        if step_key:
            steps = _tasks[task_id].setdefault("steps", [])
            # Avoid duplicate consecutive steps
            if not steps or steps[-1].get("key") != step_key:
                steps.append({
                    "key": step_key,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                })

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    return _tasks.get(task_id)
