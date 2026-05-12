# Tài liệu Đặc tả API (API Specification / OpenAPI)

Tài liệu này xác định giao thức giao tiếp chuẩn (JSON/REST) giữa Android Client và FastAPI Backend. Hệ thống sử dụng chuẩn OpenAPI 3.0.

## 1. Authentication & Security

### 1.1. Cơ chế JWT (JSON Web Token)
Tất cả các API (ngoại trừ `/auth/*`) đều yêu cầu xác thực bằng Header:
`Authorization: Bearer <access_token>`

- **Access Token:** Hết hạn sau 30 phút. Thuật toán HS256 với `SECRET_KEY`.
- **Refresh Token:** Hết hạn sau 7 ngày. Dùng để lấy lại access token mới mà không cần user đăng nhập lại.

### 1.2. Android AuthInterceptor
Phía Android sử dụng thư viện `OkHttp`. Cấu hình một `Interceptor` để:
1. Đính kèm Header Authorization vào mọi request.
2. Nếu Backend trả về HTTP `401 Unauthorized`, interceptor sẽ tự động giữ request gốc lại (Lock), gọi API `/auth/refresh` để lấy token mới, lưu vào SharedPreferences, và tự động Retry request gốc. Nếu Refresh token cũng hết hạn, force logout user về màn hình Login.

## 2. API Endpoints Chính

### 2.1. Authentication
**POST `/auth/login`**
- **Content-Type:** `application/x-www-form-urlencoded`
- **Request:** `username` (email), `password`
- **Response (200 OK):**
```json
{
  "access_token": "eyJh...",
  "refresh_token": "eyJh...",
  "token_type": "bearer"
}
```

### 2.2. Documents (Dành cho Giáo viên/Admin)
**POST `/documents/upload`**
- **Content-Type:** `multipart/form-data`
- **Request:** `file` (File object, hỗ trợ .pdf, .docx, .txt), `subject` (string, ví dụ "Toán 10")
- **Response (202 Accepted):**
```json
{
  "document_id": "uuid-1234",
  "status": "processing",
  "message": "Document is being ingested in background."
}
```

### 2.3. Graph Retrieval (Lấy dữ liệu Đồ thị)
**GET `/graph-rag/topics/{subject}`**
- **Description:** Trả về danh sách nodes và edges để Android vẽ bản đồ.
- **Response (200 OK):**
```json
{
  "nodes": [
    {
      "id": "node-1",
      "label": "Mặt phẳng",
      "mastery_level": 3
    },
    {
      "id": "node-2",
      "label": "Đường thẳng chéo nhau",
      "mastery_level": 0
    }
  ],
  "edges": [
    {
      "source": "node-1",
      "target": "node-2",
      "type": "PREREQUISITE"
    }
  ]
}
```

### 2.4. Quiz Assessment (Hệ thống Câu hỏi)
**POST `/quiz/generate`**
- **Description:** Yêu cầu LLM sinh câu hỏi dựa theo độ khó và node hiện tại.
- **Request (JSON):**
```json
{
  "topic_id": "node-2",
  "cognitive_level": "analyze",
  "question_count": 5
}
```
- **Response (200 OK):**
```json
{
  "quiz_id": "quiz-999",
  "questions": [
    {
      "id": "q-1",
      "content": "Vì sao hai đường thẳng chéo nhau lại không thể cùng nằm trên một mặt phẳng?",
      "options": [
        "A. Vì chúng cắt nhau",
        "B. Theo định lý...",
        "C. Khác mặt phẳng",
        "D. Song song"
      ],
      "bloom_level": "analyze"
    }
  ]
}
```

**POST `/quiz/submit`**
- **Description:** Nộp mảng đáp án, Backend sẽ chấm và cập nhật Graph của user.
- **Request (JSON):**
```json
{
  "quiz_id": "quiz-999",
  "answers": [
    {"question_id": "q-1", "selected_option": "B"}
  ]
}
```
- **Response (200 OK):**
```json
{
  "score": 80,
  "passed": true,
  "skill_level_up": true,
  "new_skill_level": 2,
  "prerequisites_to_review": [] 
}
```
*(Nếu passed = false, mảng `prerequisites_to_review` sẽ chứa các ID của node cần học lại).*
