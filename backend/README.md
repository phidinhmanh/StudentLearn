# StudentLearning - GraphRAG Backend

Hệ thống Backend cho ứng dụng cá nhân hóa lộ trình học tập dựa trên Knowledge Graph (GraphRAG), sử dụng FastAPI, Neo4j và Google Gemini.

## 🚀 Tính năng chính
- **Trích xuất Knowledge Graph**: Tự động phân tích tài liệu (PDF, DOCX, TXT) để xây dựng bản đồ khái niệm.
- **AI Quiz Generation**: Tạo câu hỏi kiểm tra kiến thức tự động từ đồ thị kiến thức.
- **Lộ trình học tập (Learning Path)**: Gợi ý lộ trình học cá nhân hóa dựa trên lỗ hổng kiến thức.
- **Hệ thống đánh giá**: Theo dõi tiến độ và trình độ kỹ năng của người dùng (Skill level 1-3).

## 🛠️ Công nghệ sử dụng
- **Framework**: FastAPI
- **Database**: Neo4j (Graph Database)
- **AI Engine**: Google Gemini 1.5 Flash (via LangChain)
- **Auth**: JWT (OAuth2 with Password flow)
- **Parsing**: PyMuPDF, python-docx

## 📋 Yêu cầu hệ thống
- Python 3.9+
- Neo4j Database (Local hoặc Cloud)
- Google Gemini API Key

## ⚙️ Cài đặt với uv

`uv` là cách được khuyến nghị để chạy project này vì cài dependency nhanh hơn và quản lý môi trường gọn hơn.

1. **Cài uv** nếu máy chưa có:
   ```bash
   pip install uv
   ```

2. **Tạo môi trường ảo và cài dependencies:**
   ```bash
   cd backend
   uv venv
   uv pip install -r requirements.txt
   ```

3. **Cấu hình môi trường:**
   Tạo file `.env` từ mẫu `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Cập nhật các thông số trong `.env`:
   - `GEMINI_API_KEY`: Key từ [Google AI Studio](https://aistudio.google.com/)
   - `NEO4J_URI`: Địa chỉ instance Neo4j (mặc định: `bolt://localhost:7687`)
   - `NEO4J_USER`, `NEO4J_PASSWORD`: Thông tin đăng nhập Neo4j

## 🏃 Chạy ứng dụng

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API sẽ chạy tại: `http://localhost:8000`
- Tài liệu API (Swagger UI): `http://localhost:8000/docs`

## 🧪 Chạy Tests

Hệ thống đã được tích hợp bộ test đầy đủ (Unit, Integration, API) sử dụng `pytest`. Các bài test sử dụng mock cho Neo4j và Gemini nên không cần kết nối thật khi test.

**Chạy tất cả các test:**
```bash
uv run pytest
```

**Chạy theo nhóm:**
```bash
# Chỉ Unit tests
uv run pytest tests/unit/

# Chỉ Integration tests
uv run pytest tests/integration/

# Chỉ API tests
uv run pytest tests/api/
```

**Chạy file test cụ thể:**
```bash
uv run pytest tests/unit/test_document_parser.py
```

**Chạy test verbose:**
```bash
uv run pytest -v
```

## 📂 Cấu trúc thư mục
- `app/auth/`: Xử lý xác thực và JWT.
- `app/routers/`: Các endpoint API (Documents, Quiz, Progress...).
- `app/services/`: Logic nghiệp vụ chính (Parser, Extractor, Engine).
- `app/models/`: Định nghĩa Pydantic schemas.
- `app/test_ui/`: Module Streamlit UI để test cho học sinh lớp 10.
- `tests/`: Bộ test suite 166 bài test.

## 🖥️ Module Streamlit UI Test

Module test UI cho học sinh lớp 10, giao diện wizard 5 bước: Upload → Topics → Quiz → Result → Learning Path.

### Cài đặt
```bash
# Cài streamlit và requests (đã có trong requirements.txt)
uv pip install streamlit requests
```

### Chạy
```bash
# Terminal 1: Chạy backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Chạy Streamlit UI
streamlit run app/test_ui/app.py
```

Sau đó mở trình duyệt tại `http://localhost:8501`.

### Tài khoản demo
- **Email**: `student10.demo@example.com`
- **Password**: `student10demo`

Module tự động tạo tài khoản demo khi đăng nhập lần đầu.

### Cấu trúc module
- `app/test_ui/app.py` — Entry point
- `app/test_ui/config.py` — Cấu hình backend URL và demo credentials
- `app/test_ui/components/layout.py` — Sidebar + step indicator
- `app/test_ui/components/helpers.py` — API call wrappers
- `app/test_ui/pages/` — 5 trang wizard tương ứng 5 bước

### Môi trường (tùy chọn)
Có thể cấu hình qua biến môi trường:
```bash
export STREAMLIT_BACKEND_URL=http://localhost:8000
export STREAMLIT_DEMO_EMAIL=student10.demo@example.com
export STREAMLIT_DEMO_PASSWORD=student10demo
```

## 📝 Ghi chú phát triển
- Tài liệu tải lên giới hạn 100MB.
- Quiz được cache lại sau khi tạo lần đầu cho mỗi Topic.
- Learning Path sẽ được cập nhật lại khi người dùng hoàn thành bài đánh giá mới.
