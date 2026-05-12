# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

StudentLearn — Android app + FastAPI backend giúp học sinh THPT xác định lỗ hổng kiến thức & nhận gợi ý lộ trình học cá nhân hóa qua knowledge graph.

---

## Architecture

### Android App (Kotlin + Jetpack Compose + MVVM + Hilt)

```
app/src/main/java/com/knowledgemap/app/
├── data/
│   ├── local/          # Room DB (entities, DAOs, KnowledgeMapDatabase)
│   ├── remote/         # GeminiGraphExtractor, CogneeApiService
│   ├── repository/     # GraphRepository (local + remote aggregation)
│   └── utils/          # TextChunker, GraphValidator, QuizParser
├── domain/
│   ├── model/          # TopicNode, TopicEdge, AssessmentResult, Recommendation
│   └── usecase/        # AssessmentUseCase, RecommendationEngine, SessionLoggerUseCase
├── di/                 # Hilt modules (DatabaseModule, ApiModule, NetworkModule)
└── ui/
    ├── theme/          # Color, Type, Shape, Theme
    ├── components/     # ModernComponents
    ├── navigation/     # NavGraph
    └── screen/         # Onboarding, KnowledgeMap, Assessment, Recommendation, SessionLogger
```

### Python Backend (FastAPI)

```
backend/app/
├── main.py              # FastAPI entrypoint
├── config.py            # Settings from .env
├── auth/                # JWT auth (router.py, service.py, dependencies.py)
├── routers/             # documents, quiz, learning_path, user_progress, graph_rag
├── services/            # graph_extractor, quiz_generator, learning_path_engine,
│                        # assessment_engine, cognee_service, cognee_engine,
│                        # graph_rag_service, base_graph_service, factory, task_manager
├── models/              # Pydantic schemas
└── utils/               # gemini_client, rate_limiter, diagnostic, quota_relief
```

---

## Services & Ports

| Service | Port | Command |
|---------|------|---------|
| Backend API | **7000** | `uv run uvicorn app.main:app --host 0.0.0.0 --port 7000` |
| Neo4j Browser | 7474 | Docker: `neo4j:5-community` |

Default backend port: **7000** (configured in `backend/.env.example`).

---

## Data Flow

1. **Ingest**: Upload tài liệu → FastAPI → Gemini extract → Neo4j knowledge graph
2. **Quiz**: Request → FastAPI → LLM sinh câu hỏi → đánh giá → update skill_level
3. **Recommendation**: Tính điểm ưu tiên: prerequisite gaps → ready topics → review topics
4. **GraphRAG**: Query knowledge graph → Cognee orchestration → synthesized answer

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Android | Kotlin + Jetpack Compose + MVVM + Hilt |
| Backend | FastAPI + LangChain |
| LLM | Gemini 1.5 Flash / OpenRouter (Llama 3.3) |
| Graph DB | Neo4j (Docker) |
| Local DB | Room (Android) |
| Auth | JWT (python-jose, passlib) |

---

## Knowledge Graph Schema

- **Nodes**: `topic_node` with `skill_level` ∈ {0, 1, 2, 3} (0=Xám/Locked, 1=Đỏ, 2=Vàng, 3=Xanh).
- **Edges**: `topic_edge` with relations: `prerequisite`, `sequenceOf`, `relatedTo`.
- **Constraint**: Topics are "locked" if transitive prerequisites have `skill_level` < 2.

---

## Development Commands

### Android (Root Directory)
```bash
./gradlew.bat assembleDebug   # Build Debug APK
./gradlew.bat clean            # Clean build
./gradlew.bat test             # Unit tests
./gradlew.bat testDebugUnitTest --tests "com.knowledgemap.app.domain.usecase.RecommendationEngineTest"
./gradlew.bat connectedAndroidTest  # Instrumented tests
adb install -r app/build/outputs/apk/debug/app-debug.apk  # Install APK
```

### Python Backend (`/backend`)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uv run uvicorn app.main:app --host 0.0.0.0 --port 7000
```

### Health Check
```bash
curl http://localhost:7000/api/v1/health
```

### Neo4j (Docker)
```bash
docker run -d --name studentlearn-neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH='neo4j/your_password' neo4j:5-community
```
Password must match `NEO4J_PASSWORD` in `backend/.env`.

---

## Key Logic & Constraints

- **Scoring (FR-13)**: 0-1 correct → L1, 2-3 correct → L2, 4-5 correct → L3.
- **Self-Rating (FR-22)**: Hiểu rõ → +1 skill, Chưa hiểu → -1 skill, Cần ôn tập → 0 change.
- **Recommendation (FR-17)**: Priority order: 1. Prerequisite gaps, 2. Ready to learn (all prereqs met), 3. Review (L1/L2 topics).
- **Performance**: Recommendation engine must run in < 2s offline.
- **Data Safety**: Never delete assessment history automatically (FR-24).
- **Seeding**: Initial graph loaded from `assets/toan10_graph.json` via `DatabaseModule` on first launch.

---

## Key Implementation Notes (Backend)

- **Async LLM Calls**: Always wrap `llm.invoke()` with `await asyncio.to_thread(llm.invoke, prompt)` in `async def` to avoid blocking the event loop.
- **Neo4j Lazy Init**: Driver is lazy-initialized in `neo4j_service.py` so the app doesn't crash if the DB is unavailable.
- **Many-to-Many**: Topic ↔ Document via `:FROM_DOC` edge, fuzzy match by name to reuse existing topics.
- **Quiz Caching**: Quiz generated once per topic, stored in Neo4j.
- **UTF-8 Output**: On Windows, use `sys.stdout` with `utf-8` encoding for Vietnamese display.

---

## Environment Variables (`backend/.env`)

```
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=llama-3.3-70b-versatile
OPENROUTER_BASE_URL=https://api.groq.com/openai/v1
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your_gemini_key
MAX_FILE_SIZE_MB=100
```