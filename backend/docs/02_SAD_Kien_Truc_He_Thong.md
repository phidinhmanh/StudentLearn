# Tài liệu Kiến trúc Hệ thống (SAD - System Architecture Design)

Tài liệu này đóng vai trò là "bản đồ" kỹ thuật cho các kỹ sư phần mềm, giải thích cách thức các thành phần trong StudentLearn liên kết và giao tiếp với nhau.

## 1. Sơ đồ Khối (High-Level Architecture)

Hệ thống hoạt động theo mô hình Client-Server hiện đại, chia làm 4 lớp chính:

1. **Client Layer (Android App):**
   - Viết bằng Kotlin & Jetpack Compose.
   - Quản lý UI, State (ViewModel/MVI), và Local Cache (Room DB).
2. **API Gateway & Business Logic (FastAPI):**
   - Xử lý các request từ Client.
   - Chứa các Service: `AuthService`, `GraphService`, `QuizService`, `LLMService`.
   - Xử lý Background Tasks (Ingest tài liệu async để không block thread).
3. **Graph Storage Layer (Kuzu qua thư viện Cognee):**
   - Cơ sở dữ liệu đồ thị, lưu trữ các Node (Khái niệm) và Edge (Quan hệ).
   - Tối ưu hóa cho phép duyệt đồ thị sâu (Graph Traversal) để tìm Prerequisites.
4. **AI Engine (Gemini 1.5 Flash via LiteLLM):**
   - Nhận prompt từ Backend để xử lý NPL (Natural Language Processing).
   - Thực thi các tác vụ: Entity Extraction (Trích xuất thực thể), Quiz Generation (Tạo câu hỏi).

## 2. Luồng Dữ liệu (Data Flow Diagram)

### 2.1. Luồng Ingest (Nạp dữ liệu từ Giáo viên)
Mục tiêu: Biến tài liệu văn bản thành mạng lưới đồ thị.
1. **Upload:** Giáo viên upload file `PDF/DOCX` qua API `/documents/upload`.
2. **Parsing:** Parser module dùng `PyMuPDF`/`python-docx` để đọc raw text và chia thành các chunk (VD: 1000 tokens/chunk).
3. **Extraction:** FastAPI gọi Gemini AI với prompt yêu cầu trích xuất các Thực thể (Concept) và Quan hệ (Prerequisite/Related).
4. **Semantic Deduplication:** Thuật toán gom cụm ngữ nghĩa hợp nhất các node bị trùng (ví dụ "Đạo hàm" và "Phép tính đạo hàm").
5. **Storage:** Lưu các node và edge đã chuẩn hóa vào cơ sở dữ liệu Kuzu (thông qua Cognee).

### 2.2. Luồng Assessment (Đánh giá Học sinh)
Mục tiêu: Đánh giá và cập nhật năng lực của học sinh.
1. **Trigger:** Học sinh chọn một `Topic_ID` trên App và bấm "Làm bài".
2. **Graph Traversal:** FastAPI truy vấn Graph DB lấy context của `Topic_ID` đó cùng với các khái niệm liên quan.
3. **Quiz Generation:** Gửi context và yêu cầu độ khó (theo Bloom's Taxonomy) tới Gemini AI để sinh ra một set câu hỏi JSON chuẩn.
4. **Delivery & Answer:** Android App hiển thị câu hỏi, học sinh làm bài và Submit mảng đáp án lên `/quiz/submit`.
5. **Evaluation & Mutation:** FastAPI chấm điểm. Nếu điểm < 60%, truy vấn Graph DB tìm các node `Prerequisite` của node hiện tại và gửi về cho App (tạo Learning Path). Cập nhật `Skill_Level` của user.

## 3. Cấu trúc Đồ thị (Graph Schema)

### 3.1. Schema của Nodes (Đỉnh)
- **`Topic`**: Cấp độ cao nhất.
  - Properties: `id` (UUID), `name` (Ví dụ: "Hình học không gian"), `description`.
- **`Concept`**: Khái niệm cụ thể bên trong Topic.
  - Properties: `id` (UUID), `name` (Ví dụ: "Khoảng cách giữa hai đường thẳng chéo nhau"), `definition`, `source_doc_id`.
- **`UserNode`**: Nút đại diện cho học sinh để lưu Graph tiến độ.
  - Properties: `id` (UUID), `email`, `current_streak`.

### 3.2. Schema của Edges (Cạnh)
- **`PREREQUISITE_OF`**: (Source: Concept A) -> (Target: Concept B). 
  - Ý nghĩa: Phải học A trước khi học B. Hệ thống dùng cạnh này để lùi lại khi học sinh bị hổng kiến thức.
- **`RELATED_TO`**: (Source: Concept A) <-> (Target: Concept B).
  - Ý nghĩa: Hai khái niệm có quan hệ bổ trợ (ví dụ: Hình thoi và Hình bình hành).
- **`BELONGS_TO`**: (Source: Concept) -> (Target: Topic).
  - Ý nghĩa: Tổ chức phân cấp.
- **`HAS_SKILL`**: (Source: UserNode) -> (Target: Concept).
  - Properties trên cạnh: `skill_level` (1: Novice, 2: Intermediate, 3: Master), `last_tested_at` (Timestamp). Cạnh này biểu thị sự thông thạo của user đối với khái niệm đó.
