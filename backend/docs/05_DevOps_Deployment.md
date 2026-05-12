# Tài liệu Vận hành và Triển khai (DevOps & Maintenance Manual)

Tài liệu này cung cấp hướng dẫn thiết lập hạ tầng Cloud để chạy Backend ổn định trên **Render.com**.

## 1. Deployment Guide (Hướng dẫn Deploy trên Render)

Hệ thống sử dụng phương pháp Infrastructure as Code thông qua file `render.yaml` đặt ở thư mục gốc của repo. Khi đẩy code lên nhánh `main`, Render sẽ tự động build và deploy.

### 1.1. Cấu hình `render.yaml`
```yaml
services:
  - type: web
    name: studentlearn-backend
    env: python
    region: singapore
    buildCommand: "pip install uv && uv pip install --system -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    # Cấu hình Persistent Disk
    disk:
      name: db-data
      mountPath: /app/.cognee_system
      sizeGB: 10
```

### 1.2. Tại sao cần Persistent Disk?
Dịch vụ web thông thường (Web Service) của Render là Stateless; sau mỗi lần deploy mới hoặc restart container, dữ liệu trên ổ cứng nội bộ sẽ bị mất. Vì chúng ta sử dụng Kuzu (thông qua thư viện Cognee) để lưu dữ liệu đồ thị local (chứa trong thư mục `.cognee_system`), việc gắn Persistent Disk (Disk mount) là bắt buộc để đồ thị tri thức không bị mất đi.

## 2. Environment Variables (Biến môi trường)

Trên Dashboard của Render, vào mục **Environment**, cần thiết lập các biến bảo mật sau (Không bao giờ commit các giá trị này vào Git):

| Tên biến | Chức năng | Nguồn cấp |
|----------|-----------|-----------|
| `GEMINI_API_KEY` | Key chính để thực thi GraphRAG và sinh Quiz. | Google AI Studio |
| `OPENROUTER_API_KEY` | Fallback API Key (Dùng gọi Llama/Claude nếu Gemini hết quota). | OpenRouter.ai |
| `SECRET_KEY` | Chuỗi ký tự ngẫu nhiên, dài, dùng để ký JWT token bảo mật. | Chạy lệnh `openssl rand -hex 32` |
| `ALGORITHM` | Thuật toán mã hóa JWT. | Điền cố định: `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Thời gian sống của token. | Điền: `30` |

## 3. Monitoring & Debugging (Giám sát và Sửa lỗi)

### 3.1. Giám sát từ phía Client (Android)
- Sử dụng công cụ **Logcat** trong Android Studio.
- Setup bộ lọc (Filter): `tag:OkHttp` để xem raw request và response body dưới dạng JSON. Rất hữu ích để xem API đang trả về lỗi 422 (Validation Error) hay 500 (Server Error).
- Filter `tag:AuthInterceptor` để xem log quá trình tự động làm mới token.

### 3.2. Giám sát từ phía Server (Render Logs)
- Truy cập Render Dashboard -> Chọn service `studentlearn-backend` -> Mở tab **Logs**.
- Lọc log theo từ khóa `ERROR` hoặc `Exception`.
- Trong code FastAPI, chúng ta nên setup logger in ra `TraceID` cho mỗi request.
- Nếu background task (Ingest tài liệu) bị treo hoặc thất bại (do file PDF quá lớn hoặc Gemini chặn Rate Limit 429), log sẽ hiển thị chi tiết stacktrace của `asyncio` để phục vụ việc debug. Cấu hình cơ chế Retry-After để tự động chạy lại nếu bị Rate Limit.
