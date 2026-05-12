# ARCHITECTURE.md - StudentLearn

## 1. Tổng Quan Kiến Trúc

StudentLearn sử dụng kiến trúc **Layered (N-Tier)** với sự phân tách rõ ràng giữa presentation, business logic, và data access. Hệ thống bao gồm 3 thành phần chính: **Backend API**, **Web Admin (Streamlit)**, và **Android App**. Backend là trung tâm, cung cấp REST API cho cả mobile và web.

---

## 2. Folder Structure

### 2.1. Root Project
```
StudentLearn/
├── backend/              # FastAPI backend
│   ├── app/             # Main application
│   ├── alembic/         # DB migrations
│   ├── tests/           # Test suite
│   └── scripts/         # Devops scripts
├── frontend/            # Streamlit admin (nếu riêng folder)
├── android/             # Android native app
├── docs/               # Project documentation
├── docker-compose.yml   # Orchestration
├── .env.example         # Env template
└── README.md
```

### 2.2. Backend Structure
```
backend/
├── app/
│   ├── api/            # API routers
│   │   ├── v1/         # API version 1
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── topics.py
│   │   │   │   ├── quizzes.py
│   │   │   │   ├── submissions.py
│   │   │   │   ├── cognee.py
│   │   │   │   └── admin.py
│   │   │   ├── deps.py       # Common dependencies
│   │   │   └── router.py     # Main router aggregation
│   │   └── __init__.py
│   ├── core/           # Core functionality
│   │   ├── config.py        # Pydantic settings
│   │   ├── security.py      # JWT, hashing
│   │   ├── dependencies.py  # FastAPI Depends
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── middlewares.py   # Request middleware
│   │   └── __init__.py
│   ├── models/         # SQLAlchemy models (DB schema)
│   │   ├── user.py
│   │   ├── topic.py
│   │   ├── quiz.py
│   │   ├── submission.py
│   │   ├── knowledge_graph.py
│   │   └── __init__.py
│   ├── schemas/        # Pydantic schemas (DTO)
│   │   ├── user.py
│   │   ├── topic.py
│   │   ├── quiz.py
│   │   ├── submission.py
│   │   ├── token.py
│   │   └── __init__.py
│   ├── services/       # Business logic layer
│   │   ├── auth_service.py       # Auth logic
│   │   ├── user_service.py
│   │   ├── topic_service.py
│   │   ├── quiz_service.py
│   │   ├── submission_service.py
│   │   ├── cognee_service.py     # Cognee integration
│   │   ├── knowledge_service.py
│   │   ├── email_service.py
│   │   └── __init__.py
│   ├── utils/          # Helper functions
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   ├── pagination.py
│   │   └── __init__.py
│   ├── core_config.py  # App configuration
│   ├── database.py     # DB connection & session
│   ├── cache.py        # Redis cache client
│   └── main.py         # FastAPI application entrypoint
├── alembic/            # DB migration scripts
│   └── versions/
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── conftest.py    # pytest fixtures
├── scripts/
│   ├── deploy.sh
│   ├── backup.sh
│   └── seed_data.py
├── .env.example
├── .env
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── CHANGELOG.md
```

---

## 3. Architectural Layers

### 3.1. Presentation Layer (API Layer)
- **Responsibility**: Handle HTTP requests, authentication, validation, serialization
- **Components**:
  - FastAPI routers (`app/api/`)
  - Request/Response DTOs (`app/schemas/`)
  - API versioning (`/api/v1/`, `/api/v2/`)
  - Middleware (CORS, logging, rate limiting)
- **Flow**:
  1. Request arrives at router
  2. Dependencies injection (auth, db)
  3. Request body validation (Pydantic)
  4. Forward to service layer
  5. Response serialization

### 3.2. Business Logic Layer (Service Layer)
- **Responsibility**: Encapsulate domain logic, orchestrate workflows
- **Components**: Service classes in `app/services/`
- **Characteristics**:
  - Stateless (no instance variables)
  - Accept DTOs, return DTOs or domain models
  - Handle transactions, error handling
  - Call external services (Cognee, email)
- **Example**: `QuizService.calculate_score()`, `CogneeService.ingest_document()`

### 3.3. Data Access Layer (Repository Layer)
- **Responsibility**: CRUD operations, complex queries, data mapping
- **Components**:
  - SQLAlchemy models (`app/models/`)
  - Database session management (`app/database.py`)
  - Repository pattern (optional, can be in services)
- **Patterns**:
  - Active Record (SQLAlchemy models)
  - Repository (if needed for complex queries)

### 3.4. External Services Layer
- **Responsibility**: Integrations với third-party services
- **Components**:
  - `CogneeService`: Knowledge graph, embeddings
  - `EmailService`: SMTP/SendGrid
  - `StorageService`: S3/Cloudinary (nếu có)
  - `NotificationService`: Telegram/WebSocket

---

## 4. Data Flow Diagrams

### 4.1. Authentication Flow
```
1. Client POST /api/v1/auth/login
   ↓
2. AuthService.authenticate(email, password)
   - Verify password (bcrypt)
   - Create access & refresh tokens (JWT)
   ↓
3. Set HttpOnly secure cookie (refresh token)
   ↓
4. Return { access_token, user_info }
```

### 4.2. Quiz Submission Flow
```
1. Student POST /api/v1/quizzes/{id}/submit
   ↓
2. QuizService.submit_quiz(user_id, quiz_id, answers)
   - Validate quiz ownership & deadline
   - Calculate score via QuizGradingEngine
   - Save Submission record
   ↓
3. Update UserStats (total_score, streak)
   ↓
4. Return { score, feedback, new_badge? }
```

### 4.3. Cognee Knowledge Ingestion Flow
```
1. Teacher POST /api/v1/cognee/ingest
   ↓
2. CogneeService.ingest_document(file, metadata)
   - Rate limit check: ≤ 15 req/phút
   - Extract text (OCR nếu cần)
   - Chunk & embed (Cognee pipeline)
   - Save to knowledge graph
   ↓
3. Queue for background processing nếu heavy
   ↓
4. Return { document_id, status, chunks_processed }
```

---

## 5. Critical Design Decisions

### 5.1. FastAPI vs Django
- **Choice**: FastAPI
- **Rationale**: Async-first, performance cao, tự động API docs, nhẹ, linh hoạt hơn cho microservices architecture.

### 5.2. PostgreSQL vs MongoDB
- **Choice**: PostgreSQL
- **Rationale**: ACID compliance, relational data rõ (users, quizzes, submissions), JSONB support, mạnh mẽ cho query phức tạp.

### 5.3. Redis Usage
- **Session Storage**: Lưu session data, JWT blacklist
- **Caching**: Cache frequent queries (topics list, user profile, quiz metadata)
- **Rate Limiting**: Sliding window cho API endpoints

### 5.4. Cognee Integration Pattern
- **Wrapper Service**: CogneeService lớp wrapper quanh Cognee SDK
- **Fallback Handling**: Nếu Cognee fail, trả về empty list, không crash app
- **Rate Limiting**: 15 req/phút, enforced at service layer
- **Async Processing**: Heavy ingestion pushed to background queue

### 5.5. State Management
- **Backend**: Stateless, dependency injection, Redis cache
- **Android**: ViewModel + LiveData/StateFlow
- **Streamlit**: Session state (`st.session_state`)

### 5.6. Error Handling Strategy
```
Global Exception Handler (app/main.py)
├── HTTPException → return { "success": false, "error": detail, "status_code": code }
├── ValidationError → 422 + details
├── Database Error → 500 + log
└── Unhandled → 500 + Sentry capture
```

---

## 6. API Design Principles

### 6.1. RESTful Conventions
- **Endpoints**: Plural nouns (`/api/v1/topics`, `/api/v1/quizzes`)
- **HTTP Verbs**: GET (read), POST (create), PUT (update), DELETE (delete)
- **Status Codes**:
  - 200 OK: Success GET/PUT
  - 201 Created: Success POST
  - 204 No Content: Success DELETE
  - 400 Bad Request: Validation error
  - 401 Unauthorized: Auth required
  - 403 Forbidden: Insufficient permission
  - 404 Not Found: Resource not exist
  - 409 Conflict: Duplicate resource
  - 422 Unprocessable Entity: Validation details
  - 429 Too Many Requests: Rate limit
  - 500 Internal Server Error: Server error

### 6.2. Request/Response Format
```json
// Standard Response
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2026-05-11T10:00:00Z",
    "request_id": "uuid-here"
  }
}

// Error Response
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH_FAILED",
    "message": "Invalid credentials",
    "details": { ... }
  }
}
```

### 6.3. Pagination
- Query params: `limit` (default 20), `offset` (default 0), `sort_by`, `order`
- Response includes: `items: []`, `total`, `has_more`

### 6.4. Filtering
- Query params: `filter[key]=value` (e.g., `?filter[status]=published`)

---

## 7. Database Schema Strategy

### 7.1. Core Tables
- `users` (id, email, username, password_hash, role, created_at)
- `topics` (id, title, description, created_by, parent_id, order)
- `lessons` (id, topic_id, title, content, order)
- `quizzes` (id, topic_id, title, duration, passing_score)
- `questions` (id, quiz_id, type, content, options, correct_answer, points)
- `submissions` (id, user_id, quiz_id, score, started_at, completed_at)
- `user_answers` (id, submission_id, question_id, selected_option, is_correct)
- `knowledge_nodes` (id, cognee_id, title, type, metadata)
- `knowledge_edges` (id, source_id, target_id, relation_type, weight)

### 7.2. Indexes
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_topics_parent ON topics(parent_id);
CREATE INDEX idx_quizzes_topic ON quizzes(topic_id);
CREATE INDEX idx_submissions_user ON submissions(user_id);
CREATE INDEX idx_questions_quiz ON questions(quiz_id);
```

### 7.3. Foreign Keys & CASCADE
- User deletion → cascade delete submissions, answers
- Topic deletion → cascade delete lessons, quizzes
- Quiz deletion → cascade delete questions, submissions

---

## 8. Security Architecture

### 8.1. Authentication Flow
1. Login → verify → JWT tokens (access + refresh)
2. Access token: 30 phút, stored in memory
3. Refresh token: 7 ngày, stored in HttpOnly secure cookie
4. Refresh endpoint: `/api/v1/auth/refresh`
5. Logout: blacklist refresh token in Redis

### 8.2. Authorization (RBAC)
- Roles: `student`, `teacher`, `admin`
- Permissions:
  - Student: read own data, submit quizzes
  - Teacher: CRUD own topics/quizzes, view own class stats
  - Admin: full system access

### 8.3. Rate Limiting
- **Global**: 100 requests/phút/ip
- **Auth endpoints**: 5 attempts/phút
- **Cognee API**: 15 requests/phút (strict)
- Implemented with Redis sliding window

### 8.4. Data Protection
- Passwords: bcrypt (rounds=12)
- PII: Encrypted at rest (optional)
- Backups: Encrypted, offsite
- HTTPS: Mandatory in production

---

## 9. Caching Strategy

### 9.1. What to Cache
- **Hot Data**: Topic list, user profile, quiz metadata (TTL: 1h)
- **Knowledge Graph**: Cognee query results (TTL: 30m)
- **Leaderboard**: Top scores (TTL: 10m)
- **Counts**: Quiz attempts, topic count (TTL: 5m)

### 9.2. Cache Invalidation
- **Write-through**: Update cache on write
- **Manual purge**: Admin actions
- **Time-based**: Automatic TTL expiry

### 9.3. Redis Keys Pattern
```
cache:topic:list:all
cache:user:profile:{user_id}
cache:quiz:metadata:{quiz_id}
cache:leaderboard:weekly
```

---

## 10. Background Tasks

### 10.1. Why Background Tasks?
- Email sending (welcome, results)
- Cognee ingestion (heavy embedding)
- Analytics aggregation
- Cache warming

### 10.2. Implementation
- FastAPI `BackgroundTasks` cho fire-and-forget
- Celery cho heavy, scheduled tasks (optional, future)

---

## 11. Deployment Architecture

### 11.1. Docker Services
```yaml
services:
  postgres:
    image: postgres:15
    volumes: [pgdata:/var/lib/postgresql/data]
    env_file: .env

  redis:
    image: redis:7-alpine

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes: [./backend:/app]
    env_file: .env
    depends_on: [postgres, redis]

  frontend:
    build: ./frontend
    ports: ["8501:8501"]
    depends_on: [backend]

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    depends_on: [backend, frontend]
```

### 11.2. Render Deployment
- **Backend**: Web Service (Python)
- **Postgres**: Managed PostgreSQL
- **Redis**: Managed Redis
- **Static Files**: S3/Cloudflare R2

---

## 12. Monitoring & Observability

### 12.1. Logging
- Structured JSON logs
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Fields: `timestamp`, `level`, `message`, `module`, `user_id`, `request_id`
- Output: stdout (Docker), collected by ELK or Papertrail

### 12.2. Metrics
- Request rate, latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database connection pool usage
- Redis hit rate
- Cognee API rate limit usage

### 12.3. Health Checks
- `/health`: Liveness (OK/FAIL)
- `/health/ready`: Readiness (DB, Redis connected)

### 12.4. Error Tracking
- Sentry integration (optional but recommended)
- Capture exceptions with stack trace + context

---

## 13. Versioning Strategy

### 13.1. API Versioning
- URL versioning: `/api/v1/`, `/api/v2/`
- Backward compatible changes: increment minor version (v1.1)
- Breaking changes: major version (v2)
- Version retired after 12 months of deprecation

### 13.2. Database Migrations
- Alembic revisions autogenerated
- Never delete old migration files
- Always test migrations on staging first

---

## 14. Future Considerations

### 14.1. Microservices Migration (Phase 2)
- Split Auth service
- Separate Quiz service
- isolate Cognee ingestion worker
- Message queue (RabbitMQ/Kafka)

### 14.2. Scalability Improvements
- Database read replicas
- CDN for static assets
- API Gateway (Kong/Traefik)
- Service mesh (Istio) nếu cần

### 14.3. Enhancements
- WebSocket real-time notifications
- GraphQL API (cho complex queries)
- Multi-tenancy (school-level)
- Mobile push notifications (FCM)

---

*Last Updated: 2026-05-11*
*Maintainer: Thành (phidinhmanh)*