"""
Layer 1: E2E UI Flow Test — directly targets Streamlit multipage URL /01_Upload
"""
import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright, expect

# Force UTF-8 for stdout to handle Vietnamese characters safely
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UI_URL = "http://localhost:8501/"
PDF_PATH = os.path.join(os.path.dirname(__file__), "toan10_test.txt")
TIMEOUT_MINUTES = 30

async def run_ui_test():
    print("\n" + "="*60)
    print("LAYER 1: E2E UI FLOW TEST (PLAYWRIGHT)")
    print("="*60)

    if not os.path.exists(PDF_PATH):
        os.makedirs(os.path.dirname(PDF_PATH) or ".", exist_ok=True)
        with open(PDF_PATH, "w", encoding="utf-8") as f:
            f.write("Toan lop 10: Ham so bac hai. Giai phuong trinh bac hai dung Delta.")

    async with async_playwright() as p:
        print(f"[1] Opening browser to {UI_URL}...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(UI_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)

            # Screenshot initial state
            await page.screenshot(path="e2e_step1_landed.png")

            # Click sidebar Upload link to navigate to upload page
            print("[2] Navigating to upload page...")
            upload_nav = page.locator('a:has-text("Upload")').first
            await upload_nav.wait_for(state="visible", timeout=15000)
            await upload_nav.click()
            await asyncio.sleep(5)
            await page.screenshot(path="e2e_step2_nav_upload.png")

            # Page loaded - just wait for file uploader to be available
            print("[3] Waiting for uploader...")
            uploader = page.locator('[data-testid="stFileUploader"]')
            await uploader.wait_for(state="attached", timeout=30000)

            # Give Streamlit time to settle any overlays
            await asyncio.sleep(3)
            print(f"  Uploader ready")
            uploader = page.locator('[data-testid="stFileUploader"]')
            await uploader.wait_for(state="visible", timeout=15000)
            print("[3] File uploader found")

            # Upload file via hidden input inside the uploader
            print(f"[4] Uploading file: {PDF_PATH}")
            file_input = uploader.locator('input[type="file"]')
            await file_input.set_input_files(PDF_PATH)
            await asyncio.sleep(4)

            await page.screenshot(path="e2e_step3_uploaded.png")

            # Click using JS click to bypass Streamlit overlay
            print("[5] Clicking Upload & Extract...")
            upload_btn = page.locator('button:has-text("Upload & Extract")')
            await upload_btn.wait_for(state="attached", timeout=30000)
            await upload_btn.evaluate("el => el.click()")

            # Poll for progress / completion
            print(f"[6] Monitoring progress (max {TIMEOUT_MINUTES} min)...")
            start_time = time.time()
            last_progress = -1

            while (time.time() - start_time) < TIMEOUT_MINUTES * 60:
                # Error detection
                error_div = page.locator(
                    '[data-testid="stNotification"]:has-text("Error"),'
                    '[data-testid="stException"],'
                    '.stAlert:has-text("loi")'
                )
                if await error_div.count() > 0:
                    err_text = await error_div.first.inner_text()
                    print(f"  [FAIL] Error: {err_text[:200]}")
                    await page.screenshot(path="e2e_error.png")
                    return False

                # Progress bar
                progress_bar = page.locator('[role="progressbar"]')
                if await progress_bar.count() > 0:
                    val = await progress_bar.first.get_attribute("aria-valuenow")
                    if val:
                        curr = float(val)
                        if curr != last_progress:
                            print(f"  Progress: {curr}%")
                            last_progress = curr

                # Success check — look for "Hoan tat" or "thanh cong" in page
                body_text = await page.locator("body").inner_text()
                if "Hoan tat" in body_text or "thanh cong" in body_text.lower():
                    print("  [SUCCESS] Ingestion completed!")
                    await page.screenshot(path="e2e_success.png")
                    return True
                if "That bai" in body_text:
                    print("  [FAIL] Failure detected in UI")
                    await page.screenshot(path="e2e_fail.png")
                    return False

                await asyncio.sleep(5)

            print("  [FAIL] Timed out")
            await page.screenshot(path="e2e_timeout.png")
            return False

        except Exception as e:
            print(f"  [EXCEPTION] {e}")
            await page.screenshot(path="e2e_crash.png")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(run_ui_test())
    sys.exit(0 if success else 1)