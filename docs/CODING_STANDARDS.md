# CODING_STANDARDS.md - StudentLearn

## 1. Tổng Quan
Tài liệu này quy định các tiêu chuẩn lập trình cho project StudentLearn nhằm đảm bảo tính nhất quán, dễ bảo trì và giảm thiểu bug. Tất cả các thành viên (bao gồm AI Agents) phải tuân thủ nghiêm ngặt.

---

## 2. Quy Tắc Đặt Tên (Naming Conventions)

### 2.1. Backend (Python/FastAPI)
- **Variables & Functions**: `snake_case` (ví dụ: `user_profile`, `calculate_total_score()`).
- **Classes**: `PascalCase` (ví dụ: `UserService`, `UserSchema`).
- **Constants**: `UPPER_SNAKE_CASE` (ví dụ: `MAX_RETRY_ATTEMPTS`, `DEFAULT_PAGE_SIZE`).
- **Modules/Files**: `snake_case` (ví dụ: `auth_service.py`, `user_model.py`).
- **Database Tables**: `snake_case`, số nhiều (ví dụ: `users`, `quizzes`, `submissions`).
- **Database Columns**: `snake_case` (ví dụ: `created_at`, `user_id`).

### 2.2. Frontend (Android/Compose)
- **Variables & Functions**: `camelCase` (ví dụ: `userProfile`, `calculateTotalScore()`).
- **Classes**: `PascalCase` (ví dụ: `UserViewModel`, `QuizScreen`).
- **Constants**: `UPPER_SNAKE_CASE` (ví dụ: `API_BASE_URL`).
- **Composable Functions**: `PascalCase` (ví dụ: `UserDetailScreen`, `CustomButton`).
- **Resource IDs**: `snake_case` (ví dụ: `ic_user_avatar`, `string_login_button`).

---

## 3. Cấu Trúc Code & Style

### 3.1. Python (Backend)
- **Type Hinting**: BẮT BUỘC cho mọi function signature.
  ```python
  def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
      ...
  ```
- **Async/Await**: Sử dụng `async def` cho tất cả các endpoint và service gọi I/O (DB, API).
- **Docstrings**: Sử dụng Google Style docstrings cho các function phức tạp.
  ```python
  def calculate_score(answers: List[Answer], quiz_id: int) -> float:
      """Calculates the final score for a quiz submission.
      
      Args:
          answers: List of user answers.
          quiz_id: The ID of the quiz.
          
      Returns:
          The calculated score as a float.
      """
      ...
  ```
- **Linter**: Tuân thủ PEP 8.

### 3.2. Kotlin (Android)
- **State Management**: Sử dụng `StateFlow` hoặc `LiveData` trong ViewModel.
- **UI**: Tách biệt UI (Composables) và Logic (ViewModels).
- **Networking**: Sử dụng `Result` wrapper hoặc `Either` cho API responses.

---

## 4. Quản Lý Lỗi (Error Handling)

### 4.1. Backend Strategy
- **Không dùng Bare Except**: Tuyệt đối không dùng `except: pass`. Luôn bắt exception cụ thể.
- **Custom Exceptions**: Tạo các class exception riêng trong `app/core/exceptions.py`.
- **FastAPI HTTPException**: Chỉ raise `HTTPException` tại layer **API (Router)**.
- **Service Layer**: Raise custom exceptions, không trả về `None` để báo lỗi.
- **Global Handler**: Sử dụng `exception_handler` trong `main.py` để format lỗi đồng nhất.

### 4.2. Error Response Format
Mọi lỗi API phải trả về format sau:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { "field": "reason" }
  }
}
```

---

## 5. State Management & Data Flow

### 5.1. Backend (Stateless)
- Backend phải hoàn toàn **stateless**. Không lưu state trong memory của server.
- Sử dụng **Redis** cho session, cache và rate limiting.
- Sử dụng **Dependency Injection** (`Depends`) của FastAPI cho DB session và Auth.

### 5.2. Android (Unidirectional Data Flow - UDF)
- **Flow**: UI $\xrightarrow{Event}$ ViewModel $\xrightarrow{State}$ UI.
- ViewModel không bao giờ giữ reference đến `Context` hoặc `View`.

---

## 6. Database & Performance

### 6.1. Database Rules
- **Migrations**: Mọi thay đổi schema PHẢI thông qua Alembic. Không chạy `db.create_all()` trong prod.
- **N+1 Problem**: Sử dụng `joinedload` hoặc `selectinload` trong SQLAlchemy để tránh N+1 query.
- **Indexing**: Index tất cả các foreign keys và các column thường xuyên dùng trong `WHERE` clause.

### 6.2. Performance Optimization
- **Pagination**: Bắt buộc cho mọi endpoint trả về danh sách (limit/offset).
- **Caching**: Cache các dữ liệu ít thay đổi (ví dụ: danh sách Topic) trong Redis với TTL phù hợp.
- **Async I/O**: Sử dụng `httpx` thay vì `requests` cho async calls.

---

## 7. Git & Workflow

### 7.1. Branching Model
- `main`: Code production-ready, ổn định.
- `develop`: Integration branch cho các tính năng mới.
- `feature/feature-name`: Phát triển tính năng (branch từ `develop`).
- `bugfix/issue-name`: Sửa lỗi (branch từ `develop` hoặc `main`).

### 7.2. Commit Messages (Conventional Commits)
Format: `<type>(<scope>): <subject>`
- `feat`: Tính năng mới.
- `fix`: Sửa lỗi.
- `docs`: Thay đổi tài liệu.
- `style`: Thay đổi format code (không ảnh hưởng logic).
- `refactor`: Tái cấu trúc code.
- `test`: Thêm/sửa test.
- `chore`: Cập nhật build tasks, package manager, v.v.

Ví dụ: `feat(auth): implement JWT refresh token logic`

---

## 8. Security Checklist
- [ ] Không bao giờ commit `.env` hoặc secrets.
- [ ] Validate tất cả input từ client (Pydantic schemas).
- [ ] Hash mật khẩu bằng bcrypt (work factor $\ge$ 12).
- [ ] Kiểm tra quyền truy cập (Authorization) cho mọi endpoint sensitive.
- [ ] Sử dụng HttpOnly, Secure, SameSite cookies cho refresh tokens.
- [ ] Rate limit các endpoint nhạy cảm (Login, Register, Cognee API).

---

*Last Updated: 2026-05-11*
*Version: 1.0.0*