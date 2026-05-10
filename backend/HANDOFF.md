# StudentLearn — Zero-Error & Quota-Relief Ingestion Handoff

## 🚀 Ready to Launch

```powershell
# From /backend folder — start Backend and UI together
Start-Process -NoNewWindow .\.venv\Scripts\python.exe -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 7000"
Start-Process -NoNewWindow .\.venv\Scripts\streamlit.exe -ArgumentList "run app/test_ui/main_ui.py --server.port 8501"
```

---

## 🛡️ Quota Relief System (New)

Tự động xử lý khi hết hạn ngạch (Quota) LLM bằng cơ chế xoay vòng Model.

```bash
python test_quota_relief.py
```

**Result: ✅ 19/19 — ALL TESTS PASSED**

### 3 Trụ cột cốt lõi:
1. **Model Rotation Pool**: Tự động chuyển đổi model khi gặp lỗi 429 (Rate Limit).
   - Danh sách: `gemini/text-embedding-004` → `gemini/embedding-001` → `text-embedding-3-small`
2. **Consistency Check**: Kiểm tra tính nhất quán đồ thị. Nếu model mới không tương thích với dữ liệu cũ, hệ thống sẽ cảnh báo (tránh làm hỏng vector DB).
3. **Per-Model Rate Limiting**: Mỗi model có bộ đếm quota riêng (12 RPM cho Gemini, 60 RPM cho OpenAI). Chuyển model = Reset Quota.

---

## 🎯 Zero-Error Pipeline Verification

```bash
python final_verification.py
```

**Result: ✅ 20/20 — SUCCESS**
- Đã kiểm chứng trên 20 đoạn toán học "khó nhất" trích xuất từ PDF thực.

---

## 🛠️ Key Files

| File | Purpose |
|------|---------|
| `app/utils/quota_relief.py` | Core Quota Relief System (Rotation + Consistency + Per-model limits) |
| `test_quota_relief.py` | 19-test suite for Quota Relief (PASS) |
| `final_verification.py` | Zero-error ingestion verification on real PDF data |
| `app/utils/diagnostic.py` | System health checks (DB, LLM, Rate Limits) |

---

## 🔧 LiteLLMEmbeddingEngine — 422 Fixes

Located in `.venv/Lib/site-packages/cognee/.../LiteLLMEmbeddingEngine.py`

Key protections:
1. **Sanitizer**: Xóa ký tự điều khiển, null bytes, và chuẩn hóa LaTeX artifacts.
2. **Auto Sub-chunking**: Tự động chia nhỏ đoạn văn bản dài (>400 chars) khi gặp lỗi Context/422.
3. **Timeout**: `30s` timeout để tránh treo pipeline.

---

## 📁 System Paths & Logs

| Component | Path |
|-----------|------|
| Debug Log | `.cognee_system/debug.log` |
| Consistency Record | `.cognee_system/embedding_consistency.json` |
| Vector DB (Kuzu) | `.cognee_system/databases/kuzu_db/` |

---

## 🎉 Bàn Giao "Zero-Error & Quota-Relief"

Hệ thống hiện đã đạt trạng thái tự phục hồi (Self-healing) cao nhất:
- ✅ **Bền bỉ**: Hết Quota model này tự sang model khác.
- ✅ **An toàn**: Cảnh báo trước khi làm hỏng dữ liệu cũ.
- ✅ **Chính xác**: Xử lý mượt mà 20/20 đoạn toán học thực tế từ PDF.

Toàn bộ hệ thống đã được kiểm chứng (PASS 100% tests). Bàn giao hoàn tất!