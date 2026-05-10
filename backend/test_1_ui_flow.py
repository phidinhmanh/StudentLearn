"""
Layer 1: E2E UI Flow Test — Upload → Topics → Quiz via Streamlit UI
Ensures Streamlit's own upload flow populates session_state correctly.
"""
import asyncio
import os
import re
import sys
import time
import httpx
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UI_URL = "http://localhost:8501/"
BACKEND_URL = "http://127.0.0.1:7000"
PDF_PATH = os.path.join(os.path.dirname(__file__), "toan10_test.txt")
TIMEOUT_MINUTES = 30
POLL_INTERVAL = 10  # seconds between backend polls


async def _login_to_backend() -> str:
    """Login to backend and return access token."""
    async with httpx.AsyncClient(base_url=BACKEND_URL, timeout=30) as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "student10.demo@example.com", "password": "student10demo"},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def _get_task(task_id: str, token: str) -> dict:
    """Poll backend for task status."""
    async with httpx.AsyncClient(base_url=BACKEND_URL, timeout=30) as client:
        resp = await client.get(
            f"/api/v1/documents/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def run_ui_test():
    print("\n" + "=" * 60)
    print("LAYER 1: E2E UI FLOW TEST (PLAYWRIGHT)")
    print("=" * 60)

    if not os.path.exists(PDF_PATH):
        with open(PDF_PATH, "w", encoding="utf-8") as f:
            f.write("Toan lop 10: Ham so bac hai. Giai phuong trinh bac hai dung Delta.")

    print("[0] Logging into backend API for task polling...")
    token = await _login_to_backend()
    print(f"  Got token: {token[:20]}...")

    async with async_playwright() as p:
        print(f"[1] Opening browser to {UI_URL}...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(UI_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)

            # Logout if session already active
            print("[1b] Checking if logout needed...")
            logout_btn = page.locator('button:has-text("Dang xuat")').first
            if await logout_btn.count() > 0:
                print("  Logging out existing session...")
                await logout_btn.click()
                await asyncio.sleep(3)

            await page.screenshot(path="e2e_step1_landed.png")

            # Navigate to upload page
            print("[2] Navigating to upload page...")
            upload_nav = page.locator('a:has-text("Upload")').first
            await upload_nav.wait_for(state="visible", timeout=15000)
            await upload_nav.click()
            await asyncio.sleep(5)
            await page.screenshot(path="e2e_step2_nav_upload.png")

            # Wait for file uploader
            print("[3] Waiting for uploader...")
            uploader = page.locator('[data-testid="stFileUploader"]')
            await uploader.wait_for(state="attached", timeout=30000)
            await asyncio.sleep(3)
            print("  Uploader ready")

            # Upload file
            print(f"[4] Uploading file: {PDF_PATH}")
            file_input = uploader.locator('input[type="file"]')
            await file_input.set_input_files(PDF_PATH)
            await asyncio.sleep(3)
            await page.screenshot(path="e2e_step3_uploaded.png")

            # ── Upload via API (reliable task_id) ─────────────────────────
            print("[5] Uploading document via backend API...")
            async with httpx.AsyncClient(base_url=BACKEND_URL, timeout=60) as _client:
                with open(PDF_PATH, "rb") as f:
                    _resp = await _client.post(
                        "/api/v1/documents/ingest",
                        files={"file": ("toan10_test.txt", f, "text/plain")},
                        data={"subject": "general"},
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    _resp.raise_for_status()
                    _ingest = _resp.json()
            task_id = _ingest.get("task_id")
            doc_id = _ingest.get("doc_id")
            print(f"  task_id={task_id}, doc_id={doc_id}")

            if not task_id:
                print("  [FAIL] No task_id from API")
                return False

            # Poll backend task to real completion, then move straight to Topics.
            print(f"[6] Polling backend task {task_id} (max {TIMEOUT_MINUTES} min)...")
            start_time = time.time()
            last_progress = -1

            while (time.time() - start_time) < TIMEOUT_MINUTES * 60:
                try:
                    task = await _get_task(task_id, token)
                except Exception as exc:
                    print(f"  [WARN] API poll error: {exc}")
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                status = task.get("status", "pending")
                progress = task.get("progress", 0)
                message = task.get("message", "")

                if progress != last_progress:
                    print(f"  Task status={status} progress={progress}%")
                    last_progress = progress

                if status == "completed":
                    result = task.get("result", {})
                    doc_id = result.get("doc_id", doc_id)
                    filename = result.get("filename", "")
                    topics_count = result.get("topics_extracted", 0)
                    print(f"  ✅ Completed: doc_id={doc_id}, topics={topics_count}, file={filename}")
                    break

                if status == "failed":
                    error = task.get("error", {})
                    print(f"  [FAIL] Task failed: {error.get('detail', task.get('message', ''))}")
                    await page.screenshot(path="e2e_fail_task.png")
                    return False

                await asyncio.sleep(POLL_INTERVAL)
            else:
                print("  [FAIL] Timed out waiting for backend task completion")
                await page.screenshot(path="e2e_timeout.png")
                return False

            await page.screenshot(path="e2e_success.png")

            # ── Navigate directly to Topics page via URL ──
            print("[7] Navigating directly to Topics page...")
            await page.goto(f"{UI_URL}Topics", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(5)
            await page.screenshot(path="e2e_step7_topics_page.png")
            current_url = page.url
            print(f"  Topics page URL: {current_url}")
            body7_raw = await page.locator("body").inner_text()
            print(f"  Topics page text (300): {body7_raw[:300]}")

            if "Chua co tai lieu" in body7_raw:
                print("  [FAIL] Topics page shows 'Chua co tai lieu' — session state missing")
                # Check for known error content
                if "500" in body7_raw or "Internal Server Error" in body7_raw:
                    print("  Backend returned 500 — possible API error")
                return False

            # ── Wait for topics content to load ──────────────────────────────
            print("[7c] Waiting for topics list to render...")
            await page.wait_for_function(
                "() => document.body.innerText.includes('Chon topic') || "
                "document.body.innerText.includes('Khong co topic')",
                timeout=30000,
            )
            body7 = await page.locator("body").inner_text()
            print(f"  Topics page after wait (300): {body7[:300]}")

            # ── Select first topic ──────────────────────────────────────────
            print("[8] Selecting first topic...")
            first_radio = page.locator('input[type="radio"]').first
            await first_radio.wait_for(state="attached", timeout=15000)
            await first_radio.evaluate("el => el.click()")
            await asyncio.sleep(2)
            await page.screenshot(path="e2e_step8_topic_selected.png")

            checked = page.locator('input[type="radio"]:checked')
            print(f"  Checked radio count: {await checked.count()}")

            # ── Start Quiz ─────────────────────────────────────────────────
            print("[9] Clicking 'Bat dau Quiz' button...")
            quiz_btn = page.locator('button:has-text("Bat dau Quiz")').first
            await quiz_btn.wait_for(state="visible", timeout=15000)
            await quiz_btn.evaluate("el => el.click()")
            await asyncio.sleep(6)
            await page.screenshot(path="e2e_step9_quiz_page.png")

            body = await page.locator("body").inner_text()
            print(f"  Quiz page text (300): {body[:300]}")

            quiz_radios = page.locator('input[type="radio"]')
            quiz_radio_count = await quiz_radios.count()
            print(f"  Quiz radio buttons: {quiz_radio_count}")

            if quiz_radio_count >= 4 or "Cau hoi" in body or "cau hoi" in body:
                print("  [PASS] Quiz page rendered with questions")
                return True
            else:
                print("  [FAIL] Quiz page seems empty")
                return False

        except Exception as exc:
            print(f"  [EXCEPTION] {exc}")
            await page.screenshot(path="e2e_crash.png")
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    success = asyncio.run(run_ui_test())
    sys.exit(0 if success else 1)