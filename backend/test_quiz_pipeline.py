"""
End-to-end test for quiz generation pipeline.
Run from backend/ directory with venv activated.

Usage:
    python test_quiz_pipeline.py

Preconditions:
    - Neo4j running at bolt://localhost:7687
    - Backend running at http://localhost:8000
    - At least one document + topics exist in DB (or will be created)
"""
import sys
import json
import uuid
import asyncio
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── LLM / service layer test (no server needed) ──────────────────────────────
async def test_llm_direct():
    """Test LLMWithFallback at the service layer."""
    from app.utils.gemini_client import get_llm

    print("\n─── LLM Direct Test ───────────────────────────────")
    llm = get_llm(temperature=0.3)

    prompt = "Reply with exactly one word: hello"
    try:
        response = await asyncio.to_thread(llm.invoke, prompt)
        content = response.content.strip()
        print(f"  Status:   OK")
        print(f"  Response: {content[:100]}")
        return True
    except Exception as exc:
        print(f"  Status: FAILED — {exc}")
        return False


async def test_quiz_generator_direct():
    """Test quiz_generator.generate_quiz without HTTP."""
    from app.services.quiz_generator import generate_quiz
    from app.services.cognee_service import get_cognee_service

    print("\n─── Quiz Generator Direct Test ───────────────────")
    cognee = get_cognee_service()

    # Get first available topic
    topics = await cognee.get_all_topics()
    if not topics:
        print("  Skipped — no topics in DB. Upload a document first.")
        return False

    topic = topics[0]
    tid = topic["id"]
    print(f"  Testing with topic: {topic.get('name', tid)} (id={tid})")

    try:
        result = await generate_quiz(tid)
        questions = result.get("questions", [])
        print(f"  Status:    OK")
        print(f"  Quiz ID:   {result.get('quiz_id', '?')}")
        print(f"  Questions: {len(questions)}")

        if questions:
            q = questions[0]
            print(f"  Sample Q:  {q.get('text', '')[:80]}")
            # Ensure correct_answer NOT leaked to client
            assert "correct_answer" not in q, "correct_answer leaked!"
            print(f"  No correct_answer leaked: PASS")
        return True
    except Exception as exc:
        print(f"  Status: FAILED — {exc}")
        return False


async def test_assessment_engine_direct():
    """Test assessment_engine.evaluate_quiz without HTTP."""
    from app.services.assessment_engine import evaluate_quiz
    from app.services.cognee_service import get_cognee_service

    print("\n─── Assessment Engine Direct Test ────────────────")
    cognee = get_cognee_service()

    # Find any quiz in DB
    topics = await cognee.get_all_topics()
    if not topics:
        print("  Skipped — no topics in DB.")
        return False

    quiz = await cognee.get_quiz_by_topic(topics[0]["id"])
    if not quiz or not quiz.get("questions"):
        print("  Skipped — no cached quiz found. Run quiz generator first.")
        return False

    qids = [q.get("id") or q.get("question_id", f"q{i}")
            for i, q in enumerate(quiz["questions"])]

    # Simulate all answers = "A" (random)
    answers = [{"question_id": qid, "answer": "A"} for qid in qids]
    user_id = f"test-user-{uuid.uuid4().hex[:8]}"

    try:
        result = await evaluate_quiz(user_id, quiz["quiz_id"], answers)
        print(f"  Status:     OK")
        print(f"  Score:      {result.get('score', '?')}/{result.get('total', '?')}")
        print(f"  Skill delta: {result.get('skill_level_change', '?')}")
        return True
    except Exception as exc:
        print(f"  Status: FAILED — {exc}")
        return False


# ── HTTP layer test ───────────────────────────────────────────────────────────
async def test_quiz_http():
    """Full HTTP round-trip: register → login → get quiz → submit."""
    import httpx

    print("\n─── Quiz HTTP Round-Trip Test ────────────────────")
    base = "http://localhost:8000/api/v1"
    email = f"e2e-{uuid.uuid4().hex[:8]}@test.local"
    password = "TestPass123!"

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Register
        r = await client.post(f"{base}/auth/register", json={
            "email": email, "password": password, "name": "E2E Tester"
        })
        if r.status_code in (200, 201):
            print(f"  [1] Register:  OK ({r.status_code})")
        elif r.status_code == 409:
            print(f"  [1] Register:  Already exists, continuing ({r.status_code})")
        else:
            print(f"  [1] Register:  {r.status_code} — {r.text[:120]}")
            return False

        # 2. Login
        r = await client.post(f"{base}/auth/login", data={
            "username": email, "password": password
        })
        if r.status_code != 200:
            print(f"  [2] Login:     FAILED {r.status_code} — {r.text[:120]}")
            return False
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"  [2] Login:     OK (token={token[:20]}...)")

        # 3. List documents to find topic
        r = await client.get(f"{base}/documents/", headers=headers)
        if r.status_code != 200:
            print(f"  [3] List docs: FAILED {r.status_code}")
            return False
        docs = r.json()
        print(f"  [3] List docs: OK ({len(docs)} docs)")

        if not docs:
            print("  No documents found. Upload a PDF first.")
            return False

        doc_id = docs[0]["document_id"]
        r = await client.get(f"{base}/documents/{doc_id}/topics", headers=headers)
        if r.status_code != 200:
            print(f"  [4] Get topics: FAILED {r.status_code}")
            return False
        topics = r.json()
        print(f"  [4] Get topics: OK ({len(topics)} topics)")

        if not topics:
            print("  No topics in document. Upload a richer PDF.")
            return False

        topic_id = topics[0]["topic_id"]

        # 4. Generate/get quiz via HTTP
        r = await client.get(f"{base}/quiz/{topic_id}", headers=headers)
        if r.status_code == 503:
            print(f"  [5] Get quiz:  SERVICE UNAVAILABLE — {r.text[:100]}")
            return False
        if r.status_code != 200:
            print(f"  [5] Get quiz:  {r.status_code} — {r.text[:120]}")
            return False

        quiz = r.json()
        questions = quiz.get("questions", [])
        print(f"  [5] Get quiz:  OK (quiz_id={quiz.get('quiz_id','?')}  q={len(questions)})")

        if not questions:
            print("  Quiz has 0 questions — check LLM response.")
            return False

        # 5. Submit answers
        answers = [
            {"question_id": q.get("id", f"q{i}"), "answer": "A"}
            for i, q in enumerate(questions)
        ]
        r = await client.post(
            f"{base}/quiz/submit",
            headers=headers,
            json={"quiz_id": quiz["quiz_id"], "answers": answers}
        )
        if r.status_code not in (200, 201):
            print(f"  [6] Submit:    FAILED {r.status_code} — {r.text[:120]}")
            return False

        result = r.json()
        print(f"  [6] Submit:    OK score={result.get('score')}/{result.get('total')}")
        return True


# ── Main ─────────────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="Quiz pipeline E2E tests")
    parser.add_argument("--http", action="store_true", help="Also run HTTP tests")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM direct test")
    args = parser.parse_args()

    results = {}

    if not args.skip_llm:
        results["llm"] = await test_llm_direct()

    results["quiz_gen"] = await test_quiz_generator_direct()
    results["assessment"] = await test_assessment_engine_direct()

    if args.http:
        results["http"] = await test_quiz_http()

    print("\n═══════════════════════════════════════════════════")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())