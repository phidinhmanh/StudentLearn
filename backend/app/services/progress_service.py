import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "progress_service.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id TEXT NOT NULL,
            topic_id TEXT NOT NULL,
            skill_level INTEGER NOT NULL,
            last_attempt TEXT NOT NULL,
            PRIMARY KEY (user_id, topic_id)
        )
        """)
        conn.commit()

init_db()

class ProgressService:
    async def upsert_progress(self, user_id: str, topic_id: str, skill_level: int) -> bool:
        with _get_conn() as conn:
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO progress (user_id, topic_id, skill_level, last_attempt) VALUES (?,?,?,?)",
                    (user_id, topic_id, skill_level, datetime.now().isoformat()),
                )
                conn.commit()
                return True
            except sqlite3.Error:
                return False

    async def get_user_progress(self, user_id: str):
        with _get_conn() as conn:
            cur = conn.execute("SELECT * FROM progress WHERE user_id = ?", (user_id,))
            return [dict(row) for row in cur.fetchall()]

    async def save_learning_path(self, user_id: str, path_json: str) -> bool:
        # Learning paths are more complex; for now, we store them in a separate table
        # Adding a table for paths in init_db would be better, but doing it here for consistency
        with _get_conn() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS learning_paths (user_id TEXT PRIMARY KEY, path_json TEXT, generated_at TEXT)")
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO learning_paths (user_id, path_json, generated_at) VALUES (?,?,?)",
                    (user_id, path_json, datetime.now().isoformat()),
                )
                conn.commit()
                return True
            except sqlite3.Error:
                return False

    async def get_learning_path(self, user_id: str):
        with _get_conn() as conn:
            cur = conn.execute("SELECT * FROM learning_paths WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def invalidate_learning_path(self, user_id: str):
        with _get_conn() as conn:
            conn.execute("DELETE FROM learning_paths WHERE user_id = ?", (user_id,))
            conn.commit()
