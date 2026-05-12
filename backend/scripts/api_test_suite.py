import requests
import time
import uuid
import os
import jwt
import concurrent.futures
from typing import Dict, List

BASE_URL = "http://localhost:7000/api/v1"
TEST_USER = {
    "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
    "password": "password123",
    "name": "Test User"
}

class APITestSuite:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.doc_id = None
        self.topic_id = None

    def log(self, msg: str):
        print(f"[TEST] {msg}")

    # 1. AUTH TESTS (Integration)
    def test_auth_flow(self):
        self.log("Testing Auth Flow...")
        # Register (might return token directly)
        resp = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        self.log(f"Register response: {resp.status_code}")
        assert resp.status_code == 200, f"Register failed: {resp.text}"

        # Login
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        self.log(f"Login response: {resp.status_code}")
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        data = resp.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Extract user_id from token or /me endpoint if exists
        import jwt
        decoded = jwt.decode(self.token, options={"verify_signature": False})
        self.user_id = decoded["sub"]
        self.log(f"Auth Flow OK. User ID: {self.user_id}")

    # 2. DOCUMENT & GRAPH TESTS (Integration/Acceptance)
    def test_ingest_and_graph(self):
        self.log("Testing Document Ingestion...")
        # Create dummy text file
        with open("test_doc.txt", "w", encoding="utf-8") as f:
            f.write("Toán học lớp 10 bao gồm Đại số và Hình học. Đạo hàm là một khái niệm quan trọng.")

        with open("test_doc.txt", "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/documents/ingest",
                headers=self.headers,
                files={"file": ("test_doc.txt", f, "text/plain")}
            )

        assert resp.status_code in [200, 202], f"Ingest failed: {resp.text}"
        data = resp.json()
        self.doc_id = data.get("document_id") or data.get("doc_id")
        task_id = data.get("task_id")

        if task_id:
            self.log(f"Processing task {task_id}...")
            # Poll for completion (max 60s)
            for _ in range(30):
                time.sleep(2)
                t_resp = requests.get(f"{BASE_URL}/documents/tasks/{task_id}", headers=self.headers)
                if t_resp.status_code == 200 and t_resp.json()["status"] == "completed":
                    self.log("Ingestion completed.")
                    break
        else:
            time.sleep(5)

        # Get topics
        resp = requests.get(f"{BASE_URL}/documents/{self.doc_id}/topics", headers=self.headers)
        self.log(f"Topics response: {resp.status_code} {resp.text[:200]}")
        assert resp.status_code == 200, f"Topics failed: {resp.text}"
        topics = resp.json()
        if topics:
            self.topic_id = topics[0]["id"]
        self.log("Ingestion & Graph OK.")

    # 3. QUIZ & PROGRESS (Acceptance)
    def test_quiz_and_progress(self):
        self.log("Testing Quiz & Progress Logic...")
        if not self.topic_id:
            self.log("Skipping Quiz test: No topic found.")
            return

        # Generate Quiz
        resp = requests.get(f"{BASE_URL}/quiz/{self.topic_id}", headers=self.headers)
        assert resp.status_code == 200
        quiz = resp.json()
        quiz_id = quiz["quiz_id"]

        # Submit Quiz (Acceptance logic: all correct = level 3)
        answers = {q["id"]: q["correct_answer"] for q in quiz["questions"]}
        submit_data = {
            "quiz_id": quiz_id,
            "topic_id": self.topic_id,
            "user_id": self.user_id,
            "answers": answers
        }
        resp = requests.post(f"{BASE_URL}/quiz/submit", headers=self.headers, json=submit_data)
        assert resp.status_code == 200
        assert resp.json()["skill_level"] == 3
        self.log("Quiz & Progress Logic OK.")

    # 4. PERFORMANCE TESTS
    def test_performance(self):
        self.log("Testing Performance (Latency)...")
        endpoints = [
            ("/health", "GET"),
            (f"/progress/{self.user_id}", "GET"),
            ("/learning-path/generate", "POST")
        ]

        for path, method in endpoints:
            start = time.time()
            if method == "GET":
                resp = requests.get(f"{BASE_URL}{path}", headers=self.headers)
            elif path == "/learning-path/generate":
                # POST /learning-path/generate expects user_id in query
                resp = requests.post(f"{BASE_URL}{path}", headers=self.headers, params={"user_id": self.user_id})
            else:
                resp = requests.post(f"{BASE_URL}{path}", headers=self.headers, json={"user_id": self.user_id})

            duration = time.time() - start
            self.log(f"{method} {path} took {duration:.2f}s")
            assert duration < 5.0, f"Slow response on {path}"

    def run_all(self):
        try:
            self.test_auth_flow()
            self.test_ingest_and_graph()
            self.test_quiz_and_progress()
            self.test_performance()
            self.log("ALL TESTS PASSED.")
        except Exception as e:
            self.log(f"TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if os.path.exists("test_doc.txt"):
                os.remove("test_doc.txt")

if __name__ == "__main__":
    suite = APITestSuite()
    suite.run_all()
