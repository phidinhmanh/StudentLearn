# Tài liệu Tích hợp Backend - KnowledgeMap

## 1. Tổng quan kiến trúc
Ứng dụng Android KnowledgeMap kết nối với Backend (Python/Cognee) để thực hiện các tác vụ xử lý ngôn ngữ tự nhiên và quản lý đồ thị kiến thức nâng cao.

- **Backend chính:** Python FastAPI (Cognee framework).
- **Giao thức:** REST API (JSON).
- **Thư viện client:** Retrofit 2 + OkHttp 3.

## 2. Cấu hình kết nối
Hệ thống mạng được cấu hình tập trung tại `NetworkModule.kt`.

- **Base URL:** `http://10.0.2.2:7000/` (Địa chỉ loopback của Android Emulator trỏ về localhost máy chủ).
- **Timeout:** 30 giây cho mỗi request.
- **Interceptor:** Sử dụng `HttpLoggingInterceptor` (level `BODY`) để debug các request và response trong môi trường phát triển.

## 3. Các API chính (CogneeApiService)

Ứng dụng giao tiếp với backend thông qua các endpoint sau:

### 3.1. Kiểm tra trạng thái (Health Check)
- **Endpoint:** `GET /api/v1/health`
- **Mục đích:** Kiểm tra backend có đang chạy và AI (Gemini) đã được cấu hình đúng hay chưa.
- **Dữ liệu trả về:** Trạng thái hệ thống, phiên bản và cấu hình AI.

### 3.2. Nạp tài liệu (Ingest)
- **Endpoint:** `POST /api/v1/ingest`
- **Mục đích:** Gửi văn bản tài liệu mới (ví dụ: nội dung chương học) để backend phân tích và trích xuất ra các Node và Edge cho đồ thị kiến thức.
- **Request Body:** 
    - `document_text`: Nội dung văn bản.
    - `chapter`: Chương học.
    - `subject`: Môn học (mặc định: "toan10").
- **Response:** Danh sách các `TopicNodeDto` và `TopicEdgeDto` được trích xuất tự động bằng AI.

### 3.3. Truy vấn ngữ cảnh (Query)
- **Endpoint:** `POST /api/v1/query`
- **Mục đích:** Thực hiện tìm kiếm ngữ nghĩa hoặc hỏi đáp dựa trên dữ liệu đã nạp.
- **Request Body:** 
    - `query`: Câu hỏi của người dùng.
    - `top_k`: Số lượng kết quả liên quan nhất cần trả về.
- **Response:** Chuỗi văn bản ngữ cảnh (`context`) và danh sách các chủ đề liên quan.

## 4. Luồng xử lý dữ liệu (Data Flow)
1. **Yêu cầu:** UI gọi Method trong `ViewModel`.
2. **Repository:** ViewModel gọi Repository, Repository sử dụng `CogneeApiService` để thực hiện network call.
3. **Chuyển đổi:** Dữ liệu nhận về từ API (`Dto` objects) sẽ được map sang Domain models trước khi đưa về UI hoặc lưu vào Local Database (Room).
4. **Lưu trữ:** Kết quả từ lệnh `ingest` thường được dùng để cập nhật bảng `topic_node` và `topic_edge` trong SQLite.

## 5. Xử lý lỗi
- Sử dụng `Response<T>` của Retrofit để kiểm tra `isSuccessful()`.
- Các lỗi kết nối (Timeout, No Internet) được log lại qua Interceptor và cần được xử lý tại tầng Repository/ViewModel để hiển thị thông báo cho người dùng.

## 6. Lưu ý cho Nhà phát triển
- Khi chạy trên thiết bị thật, cần thay đổi `BASE_URL` sang địa chỉ IP cụ thể của máy tính chạy backend trong cùng mạng LAN.
- Đảm bảo backend đã bật và cấu hình Gemini API Key để các tính năng `ingest` và `query` hoạt động chính xác.
