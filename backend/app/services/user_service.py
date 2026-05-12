import sqlite3
import os
from datetime import datetime

# Simple SQLite wrapper for user data (separate from Cognee graph)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "user_service.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        conn.commit()

# Initialize on import
init_db()

class UserService:
    async def create_user(self, user_id: str, email: str, name: str, hashed_password: str) -> bool:
        with _get_conn() as conn:
            try:
                conn.execute(
                    "INSERT INTO users (id, email, name, hashed_password, created_at) VALUES (?,?,?,?,?)",
                    (user_id, email, name, hashed_password, datetime.now().isoformat()),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    async def get_user_by_email(self, email: str):
        with _get_conn() as conn:
            cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cur.fetchone()
            return dict(row) if row else None

    async def get_user_by_id(self, user_id: str):
        with _get_conn() as conn:
            cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None
