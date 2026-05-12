# UI Logic & Integration Test Plan (QA)

## 1. Authentication Flow
- **TC-AUTH-01: Register Success**
    - Input: Valid Email, Password, Name
    - Action: Click "Đăng ký"
    - Expected: `POST 201`, Toast "Đăng ký thành công", Navigate to Login
- **TC-AUTH-02: Login Success**
    - Input: Registered credentials
    - Action: Click "Đăng nhập"
    - Expected: `POST 200`, JWT stored, Navigate to Home
- **TC-AUTH-03: Invalid Credentials**
    - Action: Click Login with wrong password
    - Expected: `POST 401`, Snackbar error "Sai tài khoản hoặc mật khẩu"

## 2. Home Screen
- **TC-HOME-01: Recommendation Navigation**
    - Action: Click on a Topic Card in "Gợi ý cho bạn"
    - Expected: Navigates to Assessment screen for that specific `topicId`
- **TC-HOME-02: Activity History Navigation**
    - Action: Click on a previous quiz in "Hoạt động gần đây"
    - Expected: Navigates to Assessment screen for the associated topic
- **TC-HOME-03: Notifications Click**
    - Action: Click Bell icon
    - Expected: Snackbar "Tính năng đang phát triển"

## 3. Knowledge Map (Sơ đồ)
- **TC-MAP-01: Topic Node Interaction**
    - Action: Click an unlocked topic node (Skill Level > 0)
    - Expected: Detail sheet opens, shows "Bắt đầu học" button
- **TC-MAP-02: Locked Topic Interaction**
    - Action: Click a greyed-out node
    - Expected: Detail sheet shows "Yêu cầu: Hoàn thành [Prerequisite]"
- **TC-MAP-03: Search Bar**
    - Action: Click Search icon
    - Expected: Snackbar "Tính năng đang phát triển"

## 4. Assessment (Nhiệm vụ)
- **TC-QUIZ-01: Load Questions**
    - Action: Enter Assessment Screen
    - Expected: `GET /api/v1/quiz/{id}` called, shows 1/5 questions, Shimmer ends
- **TC-QUIZ-02: Answer Selection**
    - Action: Click an option
    - Expected: UI highlights choice, shows explanation, enables "Tiếp tục"
- **TC-QUIZ-03: Submit & Result**
    - Action: Complete 5 questions, click "Nộp bài"
    - Expected: `POST /api/v1/quiz/submit`, Shows score (e.g. 4/5), Skill level updates (e.g. L2 -> L3)
- **TC-QUIZ-04: Network Failure**
    - Action: Submit quiz without internet
    - Expected: Error snackbar "Nộp bài thất bại", retry button visible

## 5. Document Ingestion
- **TC-INGEST-01: Upload PDF**
    - Action: Pick PDF file -> Click "Tải lên"
    - Expected: `POST /api/v1/documents/ingest` (202 Accepted), shows progress bar
- **TC-INGEST-02: Polling Status**
    - Action: Wait for extraction
    - Expected: `GET /status` returns `processing` -> `completed`, Map automatically refreshes

## 6. Session Logger (Ghi lại buổi học)
- **TC-SESSION-01: Save Rating**
    - Action: Select "Hiểu rõ" -> Click "Lưu buổi học"
    - Expected: `PUT /api/v1/progress` called, Navigate back, Skill level incremented on Map

## 7. Profile & Settings
- **TC-PROF-01: Logout**
    - Action: Click "Đăng xuất"
    - Expected: Token cleared from Prefs, Navigates back to Login screen
- **TC-PROF-02: Rename/Delete**
    - Action: Click "Đổi tên" or "Xóa tài khoản"
    - Expected: Snackbar "Tính năng đang phát triển"
