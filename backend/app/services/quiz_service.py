import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "quiz_service.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id TEXT PRIMARY KEY,
            topic_id TEXT NOT NULL,
            questions TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        conn.commit()

init_db()

class QuizService:
    async def save_quiz(self, quiz_id: str, topic_id: str, questions: list) -> bool:
        with _get_conn() as conn:
            try:
                conn.execute(
                    "INSERT INTO quizzes (id, topic_id, questions, created_at) VALUES (?,?,?,?)",
                    (quiz_id, topic_id, json.dumps(questions), datetime.now().isoformat()),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    async def get_quiz(self, quiz_id: str):
        with _get_conn() as conn:
            cur = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
            row = cur.fetchone()
            if row:
                data = dict(row)
                data["questions"] = json.loads(data["questions"])
                return data
            return None

    async def get_quiz_by_topic(self, topic_id: str):
        with _get_conn() as conn:
            cur = conn.execute("SELECT * FROM quizzes WHERE topic_id = ?", (topic_id,))
            row = cur.fetchone()
            if row:
                data = dict(row)
                data["questions"] = json.loads(data["questions"])
                return data
            return None
