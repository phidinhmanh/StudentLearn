# TASK_TEMPLATE.md - StudentLearn

---

## Thông Tin Task

| Trường | Mô Tả | Ví Dụ |
|--------|-------|-------|
| **ID** | Mã định danh duy nhất | `TASK-001` |
| **Tiêu đề** | Tóm tắt ngắn gọn | `Add JWT refresh token endpoint` |
| **Mô tả** | Chi tiết nhiệm vụ | `Implement /auth/refresh endpoint...` |
| **Assignee** | Người phụ trách | `Thành` |
| **Priority** | Mức độ ưu tiên | `High / Medium / Low` |
| **Status** | Trạng thái | `Todo / In Progress / Done / Blocked` |
| **Sprint** | Sprint number | `Sprint 3` |
| **Deadline** | Ngày hoàn thành dự kiến | `2026-05-20` |

---

## Mục Tiêu
- **Mục đích**: Làm rõ vấn đề cần giải quyết.
- **Kết quả mong đợi**: Output cụ thể, có thể đo lường được.

**Ví dụ**:
> Mục tiêu: Tăng bảo mật bằng cách thêm JWT refresh token, giúp access token tự động refresh khi hết hạn, giảm thiểu số lần user phải login lại.

---

## Acceptance Criteria (Điều Kiện Hoàn Thành)

- [ ] **Criterion 1**: Mô tả rõ ràng, có thể test được.
  - Ví dụ: `POST /api/v1/auth/refresh trả về access_token mới khi refresh_token hợp lệ (HTTP 200)`
- [ ] **Criterion 2**:
  - Sub-item nếu cần
- [ ] **Criterion 3**: Test coverage ≥ 90%.

---

## Files Liên Quan

- **Code**: Danh sách file sẽ được tạo/sửa.
  ```
  app/api/v1/endpoints/auth.py  (thêm endpoint)
  app/services/auth_service.py  (thêm logic)
  tests/integration/test_auth.py  (thêm tests)
  ```
- **Configuration**: `settings.py`, `.env.example` nếu cần.

---

## Dependencies (Phụ Thuộc)

- **Blocking**: Task nào phải hoàn thành trước?
  - `TASK-000` - JWT access token implementation hoàn thành.
- **Related**: Task liên quan (cùng feature).
  - `TASK-003` - Frontend refresh token logic.

---

## Risks & Mitigation

| Risk | Mức Độ (H/M/L) | Mitigation |
|------|----------------|------------|
| Cognee API rate limit (15 req/phút) gây lag | M | Thêm queue, batch processing |
| Migration mất dữ liệu user | H | Backup DB trước, test migration trên staging |
| Frontend không同步 refresh | M | Đảm bảo intercept 401 response |

---

## Implementation Steps (Các Bước Triển Khai)

### Phase 1: Analysis & Design
1. [ ] Đọc hiểu yêu cầu từ PRD/Issue.
2. [ ] Tra cứu code liên quan (`auth_service.py`, router).
3. [ ] Vẽ sơ đồ sequence/flowchart nếu cần.

### Phase 2: Implementation
4. [ ] **Backend**:
   - [ ] Thêm `refresh_token` field vào `TokenSchema`.
   - [ ] Tạo `refresh_token()` trong `AuthService`.
   - [ ] Thêm endpoint `POST /api/v1/auth/refresh`.
   - [ ] Viết unit tests cho service (`tests/unit/test_auth_service.py`).
   - [ ] Viếu integration tests (`tests/integration/test_auth_endpoints.py`).
5. [ ] **Android/Web Frontend**:
   - [ ] Implement token refresh logic trong HTTP client interceptor.
   - [ ] Store refresh token trong secure storage (Android Keystore/HttpOnly cookie).
6. [ ] **Database**: (nếu cần migration)
   - [ ] Tạo Alembic migration: `alembic revision --autogenerate -m "add refresh token column"`.
   - [ ] Kiểm tra migration carefully.

### Phase 3: Testing & QA
7. [ ] Run unit tests: `pytest tests/unit/ -v`.
8. [ ] Run integration tests: `pytest tests/integration/ -v`.
9. [ ] Manual test:
   - [ ] Login → access_token expires → call refresh → get new token.
   - [ ] Test với refresh_token invalid/expired → HTTP 401.

### Phase 4: Review & Deploy
10. [ ] Code review từ team member.
11. [ ] Update documentation (API docs, README nếu cần).
12. [ ] Merge vào `develop`, CI chạy pass.
13. [ ] Deploy lên staging, verify.

---

## Testing Strategy

| Loại Test | Mục Đích | Công Cụ |
|-----------|----------|---------|
| **Unit Test** | Test từng function/service | `pytest`, `unittest.mock` |
| **Integration Test** | Test API endpoint + DB | `httpx.AsyncClient`, `TestClient` |
| **Manual Test** | Verify manually nếu cần | Postman/curl |

**Test Cases Mẫu**:
```python
def test_refresh_token_success():
    # Arrange
    user = create_test_user()
    refresh_token = generate_refresh_token(user.id)
    
    # Act
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    
    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert response.json()["success"] is True
```

---

## Notes & References

- **Related PRD/Issue**: Link đến Notion/GitHub Issue.
- **API Spec**: Swagger docs sẽ auto-update.
- **Design Doc**: Nếu có, link Figma/Architecture diagram.
- **External Resources**: Cognee API docs, JWT best practices.

---

*Template Version: 1.0*
*Author: StudentLearn Team*
*Last Modified: 2026-05-11*