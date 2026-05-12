# PROJECT_BRIEF.md - StudentLearn

## 1. Tổng Quan
- **Tên Project**: StudentLearn
- **Mô Tả**: Hệ thống học tập trực tuyến dành cho sinh viên, hỗ trợ quản lý khóa học, bài giảng, bài tập, và thi trắc nghiệm.
- **Version**: 1.0.0

---

## 2. Mục Tiêu
### 2.1. Mục Tiêu Chính
- [ ] Cung cấp nền tảng học tập trực tuyến đầy đủ tính năng
- [ ] Hỗ trợ đa thiết bị (Web, Android)
- [ ] Tích hợp AI để cá nhân hóa trải nghiệm học tập
- [ ] Đảm bảo hiệu suất cao và khả năng mở rộng

### 2.2. Mục Tiêu Phụ
- [ ] Tích hợp Cognee cho quản lý kiến thức và graph-based learning
- [ ] Hệ thống quản lý người dùng và phân quyền linh hoạt
- [ ] Theo dõi tiến độ học tập và thống kê chi tiết

---

## 3. User Persona

### 3.1. Sinh Viên (Student)
- **Đặc Điểm**:
  - Tuổi: 18-25
  - Kỹ năng công nghệ: Trung bình đến cao
  - Thời gian sử dụng: Linh hoạt, chủ yếu vào buổi tối
- **Nhu Cầu**:
  - Truy cập bài giảng mọi lúc, mọi nơi
  - Làm bài tập và thi trắc nghiệm online
  - Theo dõi tiến độ học tập cá nhân
  - Nhận feedback tức thời

### 3.4. DevOps Engineer
- **Đặc Điểm**:
  - Tên: Jun
  - Kỹ năng: Intermediate đến Advanced về cloud, Docker, CI/CD
  - Thời gian: Full-time quản trị hệ thống
- **Nhu Cầu**:
  - Automated deployment pipeline
  - Infrastructure monitoring & alerting
  - Easy rollback mechanisms
  - Security compliance checks

### 3.5. Junior Developer
- **Đặc Điểm**:
  - Tên: Linh
  - Vai trò: Junior Fullstack Developer
  - Kỹ năng: Đang học FastAPI, React, PostgreSQL
  - Thời gian: Full-time phát triển
- **Nhu Cầu**:
  - Clear code examples & best practices
  - Onboarding documentation
  - Code review feedback
  - Access to dev environment setup

### 3.6. Senior Developer
- **Đặc Điểm**:
  - Tên: Minh
  - Vai trò: Senior Backend Developer
  - Kỹ năng: Expert Python, DB optimization, system architecture
  - Thời gian: Full-time tech lead
- **Nhu Cầu**:
  - Scalable & maintainable codebase
  - Advanced debugging tools
  - Performance benchmarks
  - Integration with third-party services (Cognee, SendGrid...)

### 3.7. Technical Writer
- **Đặc Điểm**:
  - Tên: Hà
  - Vai trò: Documentation Writer
  - Kỹ năng: User guides, API docs, tutorials
  - Thời gian: Part-time/Contract
- **Nhu Cầu**:
  - Up-to-date API documentation (Swagger)
  - Clear code comments (đủ cho auto-doc)
  - Step-by-step tutorials cho new features
  - Visual diagrams (architecture, flow)

### 3.8. QA Engineer
- **Đặc Điểm**:
  - Tên: Nhung
  - Vai trò: QA Engineer
  - Kỹ năng: Test automation, performance, security testing
  - Thời gian: Full-time quality assurance
- **Nhu Cầu**:
  - Comprehensive test cases (unit, integration, E2E)
  - Access to staging environment
  - Clear bug reporting templates
  - Performance metrics dashboards

### 3.9. Product Owner
- **Đặc Điểm**:
  - Tên: An
  - Vai trò: Product Owner
  - Kỹ năng: Agile, user research, backlog prioritization
  - Thời gian: Full-time product management
- **Nhu Cầu**:
  - Feature tracking dashboard
  - User feedback integration (Telegram bot, surveys)
  - Sprint planning & retrospective tools
  - Clear acceptance criteria (AC) cho mỗi task

---

## 4. Tech Stack

### 4.1. Backend
| Thành Phần | Công Nghệ | Version | Ghi Chú |
|------------|-----------|---------|---------|
| Framework | FastAPI | 0.109+ | Async, High Performance |
| Database | PostgreSQL | 15+ | Primary DB |
| Cache | Redis | 7+ | Session & Caching |
| Search | Elasticsearch | 8+ | Full-text Search |
| AI/ML | Cognee | Latest | Knowledge Graph |
| Authentication | JWT | - | Token-based Auth |
| API Docs | Swagger/OpenAPI | - | Auto-generated |

### 4.2. Frontend (Web)
| Thành Phần | Công Nghệ | Version | Ghi Chú |
|------------|-----------|---------|---------|
| Framework | Streamlit | 1.29+ | Admin Dashboard |
| UI Library | Custom | - | Tailored Design |
| State Management | Session State | - | Built-in |

### 4.3. Mobile (Android)
| Thành Phần | Công Nghệ | Version | Ghi Chú |
|------------|-----------|---------|---------|
| Framework | Android SDK | API 34+ | Native App |
| UI | Jetpack Compose | 1.5+ | Modern UI |
| Networking | Retrofit | 2.9+ | API Calls |
| Database | Room | 2.5+ | Local DB |

### 4.4. DevOps & Infrastructure
| Thành Phần | Công Nghệ | Ghi Chú |
|------------|-----------|---------|
| Containerization | Docker | Multi-container |
| Orchestration | Docker Compose | Local Dev |
| CI/CD | GitHub Actions | Automated |
| Deployment | Render | Cloud Hosting |
| Monitoring | Prometheus + Grafana | Optional |
| Logging | ELK Stack | Optional |

### 4.5. Third-Party Services
| Dịch Vụ | Mục Đích | Ghi Chú |
|---------|----------|---------|
| GitHub | Version Control | Private Repo |
| Telegram | Notifications | Bot Integration |
| Firebase | Push Notifications | Mobile |

---

## 5. Non-Functional Requirements

### 5.1. Performance
- **Response Time**: < 2s cho 95% requests
- **Throughput**: Hỗ trợ 1000+ concurrent users
- **API Latency**: < 500ms cho internal calls
- **Database Queries**: < 100ms cho 95% queries

### 5.2. Scalability
- **Horizontal Scaling**: Backend services
- **Vertical Scaling**: Database
- **Auto-scaling**: Dựa trên tải
- **Load Balancing**: Nginx/Traefik

### 5.3. Security
- **Authentication**: JWT với refresh token
- **Authorization**: RBAC (Role-Based Access Control)
- **Data Encryption**: TLS 1.3 cho tất cả traffic
- **Password Hashing**: bcrypt với salt
- **Rate Limiting**: 15 requests/phút cho Cognee API
- **Input Validation**: Tất cả inputs
- **SQL Injection**: Parameterized queries
- **XSS Protection**: Output sanitization

### 5.4. Reliability
- **Uptime**: 99.9% (3 nines)
- **Error Handling**: Graceful degradation
- **Retry Mechanism**: Cho external API calls
- **Circuit Breaker**: Ngắt kết nối khi lỗi liên tục

### 5.5. Maintainability
- **Code Coverage**: > 80% cho critical paths
- **Documentation**: Full docs cho tất cả endpoints
- **Logging**: Structured logs với level
- **Monitoring**: Health checks và metrics

### 5.6. Usability
- **UI/UX**: Thân thiện,直观
- **Accessibility**: WCAG 2.1 AA
- **Responsive Design**: Hỗ trợ tất cả thiết bị
- **Localization**: Hỗ trợ Tiếng Việt

### 5.7. Compliance
- **GDPR**: Tuân thủ bảo mật dữ liệu
- **Data Retention**: Xóa dữ liệu sau 1 năm không hoạt động
- **Backup**: Daily backups, giữ 30 ngày

---

## 6. Environment Requirements

### 6.1. Development
- **OS**: Windows 11 / macOS / Linux
- **Python**: 3.10+
- **Node.js**: 18+ (cho frontend)
- **Java**: 17+ (cho Android)
- **Docker**: 24+
- **Memory**: 8GB+ RAM
- **Storage**: 20GB+ SSD

### 6.2. Production
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4+ cores
- **Memory**: 16GB+ RAM
- **Storage**: 100GB+ SSD
- **Network**: 1Gbps+

---

## 7. Project Structure Overview
```
StudentLearn/
├── backend/           # FastAPI Backend
├── frontend/          # Streamlit Admin
├── android/           # Android App
├── docs/              # Documentation
│   ├── PROJECT_BRIEF.md
│   ├── ARCHITECTURE.md
│   ├── CODING_STANDARDS.md
│   └── TASK_TEMPLATE.md
└── docker-compose.yml
```

---

## 8. Contacts & Resources
- **Project Lead**: Thành (phidinhmanh)
- **GitHub**: https://github.com/phidinhmanh/StudentLearn
- **Documentation**: https://studentlearn-docs.vercel.app
- **Support**: Telegram @phidinhmanh

---

*Last Updated: 2026-05-11*
*Version: 1.0.0*