# Tài liệu Kiến trúc Lưu trữ Dữ liệu - KnowledgeMap

## 1. Tổng quan
Ứng dụng sử dụng chiến lược **Local-first**, ưu tiên lưu trữ và truy xuất dữ liệu trực tiếp trên thiết bị để đảm bảo tốc độ phản hồi nhanh và khả năng hoạt động ngoại tuyến.
- **Thư viện chính:** [Room Persistence Library](https://developer.android.com/training/data-storage/room) (trên nền SQLite).
- **Quản lý phụ thuộc:** [Hilt](https://developer.android.com/training/dependency-injection/hilt-android) (Dependency Injection).
- **Cấu hình:** [SharedPreferences](https://developer.android.com/training/data-storage/shared-preferences) được dùng để quản lý trạng thái khởi tạo dữ liệu.

## 2. Các thành phần chính

### 2.1. KnowledgeMapDatabase
Đây là điểm truy cập chính vào cơ sở dữ liệu SQLite của ứng dụng.
- **Tên DB:** `knowledgemap.db` (định nghĩa trong `KnowledgeMapDatabase.DATABASE_NAME`).
- **Chiến lược migration:** `fallbackToDestructiveMigration()` (Xóa và tạo mới DB khi có thay đổi schema trong giai đoạn phát triển).

### 2.2. Các bảng dữ liệu (Entities)
Dựa trên logic seeding, hệ thống bao gồm các bảng cốt lõi sau:

| Bảng | Chức năng | Các trường chính |
| :--- | :--- | :--- |
| **`topic_node`** | Lưu trữ các nút kiến thức (chủ đề) | `id`, `name`, `desc`, `difficulty`, `chapter`, `subject`, `skill_level`, `last_assessed` |
| **`topic_edge`** | Lưu trữ mối quan hệ giữa các chủ đề (liên kết đồ thị) | `from_id`, `to_id`, `relation` (ví dụ: tiền đề), `weight` |
| **`assessment_history`** | Lưu lịch sử làm bài kiểm tra/đánh giá | `id`, `node_id`, `score`, `timestamp` |
| **`session_log`** | Nhật ký các phiên học tập | `id`, `start_time`, `end_time`, `duration` |

## 3. Cơ chế Khởi tạo Dữ liệu (Data Seeding)
Ứng dụng sử dụng một quy trình tự động để nạp dữ liệu mặc định từ file cấu hình JSON.

1. **Nguồn dữ liệu:** File `assets/toan10_graph.json`.
2. **Thời điểm thực hiện:**
   - **`onCreate`:** Khi cơ sở dữ liệu được tạo lần đầu tiên.
   - **`onOpen`:** Kiểm tra nếu bảng `topic_node` trống (đề phòng trường hợp lỗi khi tạo), hệ thống sẽ tiến hành seed lại.
3. **Kỹ thuật:** Sử dụng `db.execSQL` với lệnh `INSERT OR IGNORE` để đảm bảo tính toàn vẹn và không trùng lặp dữ liệu khi nạp từ JSON.
4. **Flag đánh dấu:** Một biến `default_data_seeded` được lưu trong `SharedPreferences` để tránh việc seed dữ liệu nhiều lần không cần thiết.

## 5. Quản lý truy cập dữ liệu (DAOs)
Các Data Access Objects (DAOs) được cung cấp thông qua Hilt dưới dạng Singleton để đảm bảo hiệu năng:
- **`TopicNodeDao`**: Truy vấn danh sách bài học, tìm kiếm theo chương/môn học.
- **`TopicEdgeDao`**: Truy xuất cấu trúc đồ thị kiến thức (các bài học liên quan).
- **`AssessmentHistoryDao`**: Lưu và thống kê kết quả học tập.
- **`SessionLogDao`**: Ghi lại thời gian học tập của người dùng.

## 5. Dependency Injection (Hilt Module)
Tất cả các thành phần liên quan đến Database được cấu hình trong `DatabaseModule.kt`:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    // Cung cấp SharedPreferences
    // Cung cấp KnowledgeMapDatabase (với Callback seeding)
    // Cung cấp các DAOs cụ thể
}
```

## 6. Lưu ý cho Nhà phát triển
- **Đồ thị kiến thức:** Dữ liệu trong `topic_node` và `topic_edge` tạo thành một đồ thị có hướng (Directed Graph). Cần cẩn trọng khi chỉnh sửa file JSON trong assets vì nó ảnh hưởng trực tiếp đến cấu trúc bài học khi app mới cài đặt.
- **Mở rộng:** Nếu cần lưu trữ các cài đặt người dùng đơn giản (như Dark Mode, ngôn ngữ), hãy cân nhắc sử dụng `DataStore Preferences` (đã có sẵn trong dependencies).
