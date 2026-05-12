# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GraphRAG is a Graph-Based Retrieval-Augmented Generation system for personalized learning, built with FastAPI, Neo4j, LangChain, and Groq LLM.

## Architecture

### Backend (`backend/app/`)

**Purpose:** Upload documents (≤100MB) → Extract Knowledge Graph → AI generates Quiz → AI creates personalized Learning Path for each user.

**Components:**
- `main.py` — FastAPI entrypoint
- `config.py` — Settings from .env (OpenRouter/Groq, Neo4j, JWT)
- `auth/` — JWT authentication (register, login)
- `routers/` — API endpoints (documents, quiz, learning_path, user_progress)
- `services/` — Core business logic
  - `document_parser.py` — PDF/DOCX/TXT → text chunks
  - `graph_extractor.py` — LLM → Knowledge Graph extraction
  - `neo4j_service.py` — Neo4j CRUD operations
  - `quiz_generator.py` — AI generates quiz questions
  - `assessment_engine.py` — Evaluate quiz answers
  - `learning_path_engine.py` — AI generates personalized path
- `models/` — Pydantic schemas
- `utils/` — LLM client (ChatOpenAI-compatible, used by graph_extractor/quiz_generator/learning_path_engine)

**Tech Stack:**
| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| LLM | Groq — `llama-3.3-70b-versatile` (OpenAI-compatible via LangChain `ChatOpenAI`) |
| Graph DB | Neo4j |
| Orchestration | LangChain |
| Auth | JWT (python-jose, passlib) |
| Document Parsing | PyMuPDF, python-docx |

**Key Data Model (Many-to-Many Document ↔ Topic)**

```
(:Document)-[:FROM_DOC]->(:Topic)
(:Topic)-[:prerequisite|sequenceOf|relatedTo]->(:Topic)
(:Quiz)-[:CONTAINS]->(:Question)
(:User)-[:HAS_PROGRESS]->(:Progress)
(:User)-[:HAS_PATH]->(:LearningPath)
```

**Điểm khó**: 1 Topic có thể từ nhiều Document → fuzzy match by name → reuse existing topic

## Development Commands

### Setup (Backend)
```bash
cd backend
python -m venv .venv
# Activate: source .venv/Scripts/activate  (Windows)
pip install -r requirements.txt
```

### Neo4j (Docker)
```bash
docker run -d --name studentlearn-neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH='neo4j/your_neo4j_password' neo4j:5-community
# Default password must match NEO4J_PASSWORD in .env
```

### Running
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 7000
```

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

## API Endpoints

### Auth
- `POST /api/v1/auth/register` — Register new user
- `POST /api/v1/auth/login` — Login → JWT token

### Documents
- `POST /api/v1/documents/ingest` [JWT] — Upload & extract knowledge graph
- `GET /api/v1/documents/` [JWT] — List user's documents
- `GET /api/v1/documents/{doc_id}/topics` [JWT] — Get topics from document

### Quiz
- `GET /api/v1/quiz/{topic_id}` [JWT] — Generate/get cached quiz
- `POST /api/v1/quiz/submit` [JWT] — Submit answers → get evaluation

### Learning Path
- `GET /api/v1/learning-path/{user_id}` [JWT] — Get personalized path (cached)
- `POST /api/v1/learning-path/generate` [JWT] — Force regenerate

### Progress
- `GET /api/v1/progress/{user_id}` [JWT] — Get all topic progress
- `PUT /api/v1/progress/{user_id}/{topic_id}` [JWT] — Update self-rating

## Environment Variables (`.env`)
```
OPENROUTER_API_KEY=your_groq_or_openrouter_key
OPENROUTER_MODEL=llama-3.3-70b-versatile
OPENROUTER_BASE_URL=https://api.groq.com/openai/v1
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
JWT_SECRET_KEY=your_super_secret_key_change_this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
MAX_FILE_SIZE_MB=100
```

## Key Implementation Notes
- **Async LLM Calls**: Luôn bọc `llm.invoke()` bằng `await asyncio.to_thread(llm.invoke, prompt)` khi gọi trong `async def` để tránh chặn event loop.
- **Neo4j Lazy Init**: Driver được khởi tạo lazy tại `neo4j_service.py` để app không crash nếu DB chưa sẵn sàng.
- **UTF-8 Output**: Khi chạy script test ở terminal Windows, sử dụng `sys.stdout` với encoding `utf-8` để hiển thị đúng tiếng Việt.


## Demo Flow

1. **Register**: `POST /api/v1/auth/register` with email, password, name
2. **Login**: `POST /api/v1/auth/login` → get JWT token
3. **Ingest**: `POST /api/v1/documents/ingest` with PDF file → extracts ~10-20 topics
4. **Get Topics**: `GET /api/v1/documents/{doc_id}/topics`
5. **Generate Quiz**: `GET /api/v1/quiz/{topic_id}` → 5 questions
6. **Submit Quiz**: `POST /api/v1/quiz/submit` with answers → score + skill_level
7. **Get Learning Path**: `GET /api/v1/learning-path/{user_id}` → personalized roadmap

## Key Design Patterns

- **JWT Auth**: All protected routes require `Authorization: Bearer <token>`
- **Quiz Caching**: Quiz generated once per topic, stored in Neo4j
- **Learning Path Cached**: Generated once, invalidated on new assessment
- **Many-to-Many**: Topic ↔ Document via `:FROM_DOC` edge, fuzzy match on name

## Demo with Sample PDF

Upload a small PDF (~1-5MB) with math content to test:
- Topic extraction → creates nodes in Neo4j
- Quiz generation → 5 questions per topic
- Assessment → skill_level 1-3
- Learning path → prioritized topic list