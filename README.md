# StudentLearn

Android app + FastAPI backend giúp học sinh THPT xác định lỗ hổng kiến thức & nhận gợi ý lộ trình học cá nhân hóa qua knowledge graph.

---

## Quick Start

### Interactive Menu
```bash
chmod +x setup.sh
./setup.sh
```

| # | Option | Mô tả |
|---|--------|-------|
| 1 | Setup Android SDK | Tìm SDK, generate `local.properties` |
| 2 | Build Debug APK | `./gradlew assembleDebug` |
| 3 | Install Emulator | Tải emulator + system image, tạo AVD |
| 4 | Start Emulator | Khởi động emulator + cài APK |
| 5 | Build + Install | Build APK rồi cài lên device/emulator |
| 6 | Setup Backend | Tạo venv, pip install dependencies |
| 7 | Run Backend Server | Start uvicorn trên port 7000 |
| 8 | View Logcat (live) | Xem log trực tiếp từ app |
| 9 | Crash Log | Dump crash log + lưu vào file |
| 10 | Full Setup | Chạy 1 + 2 + 6 cùng lúc |

### CLI (non-interactive)
```bash
./setup.sh sdk        # Setup SDK
./setup.sh build      # Build debug APK
./setup.sh backend    # Setup Python backend
./setup.sh serve      # Run backend server (port 7000)
./setup.sh all        # Full setup
```

Sau khi chạy, cấu hình API keys:
1. `local.properties` → `gemini.api.key=YOUR_KEY`
2. `backend/.env` → `GEMINI_API_KEY`, `NEO4J_PASSWORD`

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Java JDK | 21+ |
| Python | 3.9+ |
| Android SDK | 34 |
| Neo4j | 5.x (Docker) |
| Gemini API Key hoặc OpenRouter Key | - |

---

## Architecture

```
├── app/                          # Android (Kotlin + Jetpack Compose)
│   └── src/main/java/com/knowledgemap/app/
│       ├── data/                 # Room DB, API clients, Repository
│       ├── domain/              # UseCases, Models
│       ├── di/                  # Hilt modules
│       └── ui/                  # Compose screens, Navigation, Theme
│
└── backend/                     # FastAPI + Neo4j
    └── app/
        ├── main.py              # FastAPI entrypoint
        ├── auth/                # JWT authentication
        ├── routers/             # API: documents, quiz, learning_path, user_progress
        ├── services/            # Graph extractor, Quiz generator, Learning path engine
        ├── models/              # Pydantic schemas
        ├── utils/               # Gemini client, rate limiter
        └── test_ui/             # Streamlit test UI (port 8501)
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| Android | Kotlin + Jetpack Compose + MVVM + Hilt |
| Backend | FastAPI + LangChain |
| LLM | Gemini 1.5 Flash hoặc OpenRouter (Llama 3.3) |
| Graph DB | Neo4j (Docker) |
| Local DB | Room (Android) |

---

## Services & Ports

| Service | Port | Command |
|---------|------|---------|
| Backend API | 7000 | `uv run uvicorn app.main:app --host 0.0.0.0 --port 7000` |
| Streamlit UI | 8501 | `streamlit run app/test_ui/main_ui.py --server.port 8501` |
| Neo4j Browser | 7474 | `docker run -p 7474:7474 -p 7687:7687 ...` |

---

## Setup Backend

```bash
cd backend

# Tạo venv và cài deps
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Cấu hình .env
cp .env.example .env
# Edit .env với NEO4J_PASSWORD, GEMINI_API_KEY

# Chạy Neo4j (Docker)
docker run -d --name studentlearn-neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH='neo4j/your_password' neo4j:5-community

# Chạy backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 7000
```

---

## Data Flow

1. **Upload tài liệu** → FastAPI → Gemini extract → Neo4j knowledge graph
2. **Quiz** → Request → Groq/Llama LLM → sinh câu hỏi → đánh giá → update skill_level
3. **Recommendation** → Tính điểm ưu tiên: prerequisite gaps → ready topics → review topics

---

## Key Constraints

- `skill_level` ∈ {0 (locked), 1 (đỏ), 2 (vàng), 3 (xanh)} — topic locked khi transitive prerequisite có skill_level < 2
- Scoring: 0-1 đúng → L1, 2-3 → L2, 4-5 → L3
- Self-rating: Hiểu rõ → +1, Chưa hiểu → -1, Cần ôn → 0
- Priority order: prerequisite gaps > ready to learn > review
- Recommendation engine phải chạy trong < 2s offline

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| SDK not found | Check `local.properties` with forward slashes (`/`) |
| Neo4j auth failed | Match password in `.env` vs Docker `NEO4J_AUTH` |
| 429 Rate Limit | Wait 24h hoặc chuyển OpenRouter provider |
| Backend 500 error | Check Neo4j datetime serialization in responses |