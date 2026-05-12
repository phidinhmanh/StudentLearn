# Kế Hoạch Refactor CogneeService

## Mục Tiêu
Refactor `CogneeService` để **thực sự dùng Cognee API** thay vì file JSON local cho việc quản lý Knowledge Graph (topics, edges, documents).

## Vấn Đề Hiện Tại
- `CogneeService` đang dùng `cognee_metadata.json` làm "database" cho tất cả metadata (users, documents, topics, edges, quizzes, progress, paths)
- Chỉ 3 hàm cuối (`ingest_text`, `search`, `recall`) mới gọi đến Cognee API
- **Không dùng Cognee để lưu trữ cấu trúc đồ thị** (nodes, edges) - điều này hoàn toàn trái với mục đích của Cognee

## Phân Tích Cognee API

Từ `cognee_engine.py`, tôi thấy các API sau đã được wrap sẵn:
- `cognee.remember(file_path, dataset_name)` - Ingest document
- `cognee.search(query_type, query_text)` - Search graph
- `cognee.visualize_graph()` - Get graph visualization
- `cognee_recall(query_text, datasets)` - Recall context (V2)

Cognee có thể:
1. **Lưu trữ documents** với metadata
2. **Tự động extract topics/concepts** từ documents
3. **Xây dựng knowledge graph** với nodes (concepts) và edges (relationships)
4. **Search RAG** trên graph
5. **Recall context** từ datasets

## Chiến Lược Refactor

### Phân Loại Dữ Liệu

| Loại Dữ Liệu | Hiện Tại | Đề Xuất | Lý Do |
|-------------|-----------|----------|-------|
| **Documents** | JSON file | Cognee `remember()` | ✅ Cognee thiết kế cho việc này |
| **Topics** | JSON file | Cognee Graph Nodes | ✅ Cognee auto-extract từ documents |
| **Edges** | JSON file | Cognee Graph Edges | ✅ Cognee auto-build relationships |
| **Users** | JSON file | ✅ **Giữ SQL/DB riêng** | ❌ Không phải knowledge, là app data |
| **Quizzes** | JSON file | ✅ **Giữ SQL/DB riêng** | ❌ Không phải knowledge |
| **Progress** | JSON file | ✅ **Giữ SQL/DB riêng** | ❌ User-specific state |
| **Paths** | JSON file | ✅ **Giữ SQL/DB riêng** | ❌ User-specific state |

### Nguyên Tắc
1. **Knowledge Graph data** (documents, topics, edges) → **Cognee**
2. **Application data** (users, quizzes, progress, paths) → **SQLite/PostgreSQL** (tách ra khỏi CogneeService)

## Kế Hoạch Chi Tiết

### Phase 1: Tách Application Data Ra Khỏi CogneeService

**Lý do:** Application data (users, quizzes, progress) không thuộc về Knowledge Graph. Việc gắn chúng vào CogneeService là sai thiết kế.

**Hành động:**
1. Tạo `UserService` mới để quản lý users
2. Tạo `QuizService` để quản lý quizzes
3. Tạo `ProgressService` để quản lý user progress
4. Cập nhật `factory.py` để inject các service này

**Files thay đổi:**
- `app/services/user_service.py` (mới)
- `app/services/quiz_service.py` (mới)
- `app/services/progress_service.py` (mới)
- `app/services/factory.py` (thêm factory functions)

### Phase 2: Refactor CogneeService Chỉ Dùng Cognee API

**Hành động:**
1. Xóa toàn bộ code liên quan đến `cognee_metadata.json`
2. Xóa các phương thức quản lý users/quizzes/progress (chuyển sang services mới)
3. Triển khai các phương thức Knowledge Graph bằng Cognee API:
   - `create_document()` → `cognee.remember()`
   - `get_documents_by_user()` → Query Cognee metadata
   - `get_document()` → Query Cognee metadata
   - `batch_upsert_topics()` → Dùng Cognee's native graph operations
   - `batch_upsert_edges()` → Dùng Cognee's native graph operations
   - `get_topics_by_document()` → Query Cognee graph
   - `get_all_topics()` → Query Cognee graph
   - `get_topic_with_neighbors()` → Query Cognee graph với relationships

**Files thay đổi:**
- `app/services/cognee_service.py` (refactor hoàn toàn)

### Phase 3: Cập Nhật BaseGraphService

**Hành động:**
1. Xóa các abstract methods không liên quan đến Knowledge Graph (users, quizzes, progress)
2. Chỉ giữ các methods liên quan đến documents, topics, edges

**Files thay đổi:**
- `app/services/base_graph_service.py`

### Phase 4: Cập Nhật GraphRAGService

**Hành động:**
1. Đảm bảo `GraphRAGService` vẫn hoạt động với `CogneeService` mới
2. Kiểm tra integration giữa Cognee search và RAG pipeline

**Files thay đổi:**
- `app/services/graph_rag_service.py` (nếu cần)

### Phase 5: Cập Nhật Routers

**Hành động:**
1. Cập nhật các router đang dùng `CogneeService` cho users/quizzes
2. Chuyển sang dùng các service mới (UserService, QuizService)

**Files thay đổi:**
- `app/routers/*.py` (cần kiểm tra)

## Rủi Ro & Giải Pháp

| Rủi Ro | Giải Pháp |
|--------|-----------|
| Cognee API không hỗ trợ query topics/edges trực tiếp | Dùng `cognee.search()` với query đặc biệt hoặc `cognee.visualize_graph()` rồi parse |
| Performance chậm khi query Cognee | Đã có `rate_limit_retry` trong `cognee_engine.py` |
| Đổi sang Cognee sẽ mất dữ liệu hiện có | Backup `cognee_metadata.json` trước, viết migration script |
| Application data chưa có DB | Dùng SQLite tạm thời, sau này chuyển sang PostgreSQL |

## Verification Steps

1. ✅ Tất cả tests vẫn pass
2. ✅ `ingest_text()` vẫn hoạt động
3. ✅ `search()` vẫn hoạt động
4. ✅ `recall()` vẫn hoạt động
5. ✅ Graph visualization vẫn hoạt động
6. ✅ User/Quiz/Progress không bị break

## Open Questions

1. Cognee có API nào để query list documents metadata?
2. Cognee có API nào để query topics/nodes trực tiếp?
3. Làm thế nào để mapping giữa Cognee's internal IDs và app's IDs?
4. Có nên giữ một layer caching (Redis) cho application data?

## Thứ Tự Ưu Tiên

1. **Phase 1** (Cao) - Tách application data ra khỏi CogneeService
2. **Phase 2** (Cao) - Refactor CogneeService dùng Cognee API
3. **Phase 3** (Trung bình) - Cập nhật BaseGraphService
4. **Phase 4** (Trung bình) - Verify GraphRAG integration
5. **Phase 5** (Thấp) - Cập nhật routers
