# UI Interaction Logic & Backend Mapping

## Auth Flow
- **Register**: `POST /api/v1/auth/register` (Email, Password, Name)
- **Login**: `POST /api/v1/auth/login` -> Store JWT in `SharedPreferences`

## Home Screen
- **Topic Cards**: Navigate to Assessment (`topicId`)
- **Activity History**: Fetch `TopicHistoryEntity`, navigate to Assessment
- **Notifications**: Snackbar stub (Future: `GET /api/v1/notifications`)

## Knowledge Map (Sơ đồ)
- **Node Click**: Show details/Locked status (based on `skillLevel` & prerequisites)
- **Search**: Snackbar stub (Future: `GET /api/v1/documents/search?q=...`)
- **Mastery Progress**: Calculate `(completed + inProgress * 0.5) / total`

## Assessment (Nhiệm vụ)
- **Load Quiz**: `GET /api/v1/quiz/{topicId}` -> Get 5 questions
- **Submit Quiz**: `POST /api/v1/quiz/submit` -> Returns `score` & `skill_level`
- **Result Logic**: Update local Room DB `skillLevel` (L1: 0-1, L2: 2-3, L3: 4-5)

## Document Ingestion
- **Upload PDF**: `POST /api/v1/documents/ingest` (Multipart File)
- **Status Check**: `GET /api/v1/documents/status/{taskId}` (Polling)
- **Fetch Graph**: `GET /api/v1/documents/{docId}/topics` -> Update Knowledge Map

## Session Logger (Ghi lại buổi học)
- **Start Session**: Local trace on `topicId`
- **Self Rating**: `PUT /api/v1/progress/{userId}/{topicId}`
- **Rating Effects**: Hiểu rõ (+1), Cần ôn lại (0), Chưa hiểu (-1)

## Profile
- **Rename/Delete Account**: Snackbar stubs (Future: `PUT /api/v1/users/me`)
- **Logout**: Clear `SharedPreferences` -> Navigate to Login
