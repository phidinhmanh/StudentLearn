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
2. `backend/.env` → `GEMINI_API_KEY`, `NEO4J_PASSWORD`, `OPENROUTER_API_KEY` (optional)

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Java JDK | 21+ |
| Python | 3.9+ |
| Android SDK | 34 |
| Neo4j (optional) | 5.x (Docker) |
| Kuzu (default graph DB) | 0.4+ (pip install) |
| Gemini API Key / OpenRouter Key | - |

---

## 🏗️ Architecture

```
├── app/                          # Android (Kotlin + Jetpack Compose)
│   └── src/main/java/com/knowledgemap/app/
│       ├── data/                 # Room DB, API clients, Repository
│       │   └── remote/
│       │       ├── StudentLearnApi.kt    # Retrofit interface (OpenAPI-aligned)
│       │       ├── AuthClient.kt         # JWT token management
│       │       ├── ApiDto.kt             # Request/Response DTOs
│       │       └── NetworkModule.kt      # Hilt + JWT interceptor
│       ├── domain/              # UseCases, Models
│       │   ├── model/
│       │   │   ├── TopicNode.kt
│       │   │   ├── TopicEdge.kt
│       │   │   ├── AssessmentResult.kt
│       │   │   ├── Recommendation.kt
│       │   │   └── DegradationTier.kt    # S/A/B/C/D tiers for learning decay
│       │   └── usecase/
│       │       ├── AssessmentUseCase.kt
│       │       ├── RecommendationEngine.kt
│       │       ├── SessionLoggerUseCase.kt
│       │       └── DegradationCalculator.kt  # Meme-based decay tracker
│       ├── di/                  # Hilt modules
│       │   ├── DatabaseModule.kt
│       │   ├── NetworkModule.kt
│       │   └── ApiModule.kt
│       └── ui/                  # Compose screens, Navigation, Theme
│           ├── theme/           # EmberComponents, Color, Type, Shape
│           ├── components/      # BottomNavigationBar, DegradationMemeCard, TopicCard
│           ├── navigation/      # BottomNavGraph (4-tab)
│           └── screen/
│               ├── HomeScreen.kt            # Animated stats, badges, degradation widget
│               ├── ProfileScreen.kt         # User profile + analytics
│               ├── KnowledgeMapScreen.kt    # Interactive graph visualization
│               ├── OnboardingScreen.kt      # 3-min max flow (NFR-09)
│               ├── AssessmentScreen.kt      # Quiz with Bloom's taxonomy
│               ├── RecommendationScreen.kt  # Top 3 personalized topics
│               └── SessionLoggerScreen.kt   # Self-rating (FR-22)

└── backend/                     # FastAPI + Cognee + Kuzu
    └── app/
        ├── main.py              # FastAPI entrypoint (v2.0.0) with CORS + JWT
        ├── config.py            # Settings from .env
        ├── auth/                # JWT authentication (router, service, dependencies)
        ├── routers/             # API endpoints (prefix: /api/v1)
        │   ├── documents.py     # Upload → extract → graph pipeline
        │   ├── quiz.py          # Generate + submit quiz
        │   ├── learning_path.py # Recommendation engine
        │   ├── user_progress.py # Session logging + skill updates
        │   └── graph_rag.py     # Cognee GraphRAG query endpoint
        ├── services/            # Business logic layer
        │   ├── graph_extractor.py    # Gemini → topic/edge extraction + semantic aggregation
        │   ├── quiz_generator.py     # Bloom's taxonomy quiz (U/A/Analyze mix)
        │   ├── learning_path_engine.py  # Priority: prereq gaps → ready → review
        │   ├── assessment_engine.py     # Skill level calculator (0-1→L1, 2-3→L2, 4-5→L3)
        │   ├── cognee_engine.py        # Kuzu + Cognee integration (v2 embedding)
        │   ├── cognee_service.py
        │   ├── graph_rag_service.py    # GraphRAG orchestration
        │   ├── base_graph_service.py
        │   ├── document_parser.py      # PyMuPDF, python-docx extraction
        │   ├── task_manager.py         # Async background ingestion tasks
        │   ├── rate_limiter.py         # Async RPM limiter for LLM/embedding
        │   ├── quota_relief.py         # Multi-model embedding pool + auto-failover
        │   ├── diagnostic.py           # Health checks + debug endpoints
        │   └── factory.py
        ├── models/              # Pydantic schemas (Document, Quiz, Topic, User)
        ├── utils/               # Infrastructure utils
        │   ├── gemini_client.py       # LiteLLM wrapper with retry logic
        │   └── [...]
        └── test_ui/             # Streamlit test UI (6-page wizard + GraphRAG)
            ├── main_ui.py
            ├── config.py
            ├── components/
            └── pages/
                ├── 01_Upload.py
                ├── 02_Topics.py
                ├── 03_Quiz.py
                ├── 04_Result.py
                ├── 05_Learning_Path.py
                ├── 04_Knowledge_Graph.py   # Graph visualization
                └── 06_GraphRAG.py          # Natural language Q&A
```

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Android App** | Kotlin + Jetpack Compose + MVVM + Hilt |
| **Backend API** | FastAPI (v2.0.0) + Uvicorn |
| **LLM (primary)** | Google Gemma 4 (26B) via Gemini API |
| **LLM (fallback)** | OpenRouter (Llama, Groq, Together.ai) |
| **Embedding** | Gemini text-embedding-004 (primary) + text-embedding-3-small (fallback) |
| **Graph DB** | Kuzu 0.4+ (embedded, serverless) |
| **Knowledge Graph Layer** | Cognee 1.0 (orchestration, retrieval, memory) |
| **Local DB (Android)** | Room (SQLite) |
| **Auth** | JWT (python-jose + passlib) |
| **Test UI** | Streamlit (multipage wizard) |

---

## 🌐 Services & Ports

| Service | Port | Command |
|---------|------|---------|
| Backend API | `7000` | `uv run uvicorn app.main:app --host 0.0.0.0 --port 7000` |
| Android Emulator | `5554` | (via Android Studio AVD Manager) |

**🚀 Production (Render):**
- Backend: `https://studentlearn-backend.onrender.com`
- Health check: `/api/v1/health`
- OpenAPI spec: `/api/v1/openapi.yaml`
- Deployment: `render.yaml` (auto-deploy from GitHub)

---

## 📋 Knowledge Graph Schema

### Nodes: `topic_node`
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | str | Standardized topic name (THPT curriculum) |
| `description` | str | LLM-generated summary |
| `subject` | str | e.g. "Toán 10", "Vật lý 12" |
| `skill_level` | int | ∈ {0,1,2,3}: 0=Gray(Locked), 1=Red, 2=Yellow, 3=Green |
| `self_rating` | int | User's self-assessment (-1/0/1) |
| `last_assessed_at` | datetime | Timestamp of last quiz |
| `prerequisites_met` | bool | Transitive prereq check result |

### Edges: `topic_edge`
| Field | Type | Description |
|-------|------|-------------|
| `source_id` → `target_id` | UUID | Directed edge |
| `relation_type` | enum | `prerequisite`, `sequenceOf`, `relatedTo` |

### Constraints (CON-*)
- **CON-D03**: Topic locked if *any* transitive prerequisite has `skill_level < 2`
- **CON-P02**: Recommendation engine ≤ 2s offline (pre-computed caches)
- **CON-A05**: All LLM outputs validated (4 required fields, skip invalid)
- **CON-A01**: LLM timeout = 10s
- **CON-S02**: Document chunks ≤ 3000 chars

---

## 🔄 Data Flow

```
┌─────────────────┐
│  Android App    │  ← User uploads PDF/DOCX/TXT
└────────┬────────┘
         │ POST /api/v1/documents/upload
         ▼
┌─────────────────────────────────────────┐
│  FastAPI (port 7000)                    │
│  1. Parse document (PyMuPDF / docx)     │
│  2. Chunk → Gemini extract (graph_extractor) │
│     - Phase 1: LLM extraction           │
│     - Phase 2: Deduplication            │
│     - Phase 3: Semantic Aggregation ⭐ │
│     - Phase 4: Batch upsert to Kuzu     │
│  3. Return topic nodes + edges          │
└────────┬────────────────────────┬────────┘
         │                        │
         ▼                        ▼
┌──────────────┐      ┌──────────────────────┐
│  Room DB     │      │  Kuzu + Cognee       │
│  (local cache│      │  (graph persistence) │
│   sync)      │      │                      │
└──────────────┘      └──────────┬───────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Quiz Generation        │
                    │  (Bloom's Taxonomy):    │
                    │  - 30% Understanding    │
                    │  - 40% Application      │
                    │  - 30% Analyze ⭐      │
                    └────────┬────────────────┘
                             │
                             ▼
                    ┌─────────────────────────┐
                    │  Recommendation Engine  │
                    │  Priority order:        │
                    │  1. Prerequisite gaps   │
                    │  2. Ready to learn      │
                    │  3. Review topics       │
                    └─────────────────────────┘
```

---

## 🎯 Key Features

### 1. Semantic Graph Aggregation (⭐ Flagship)
**Overcomes LLM overfitting** — merges semantically duplicate topics (e.g. "Venn Diagram" vs "Biểu đồ Venn") via LLM-based entity resolution into canonical THPT curriculum names.

**Pipeline** (`backend/app/services/graph_extractor.py`):
1. Extract entities/relations from text chunks
2. Basic case-insensitive dedup
3. **Semantic aggregation** — LLM resolves synonyms into unified topic
4. Batch upsert to Kuzu/Cognee

**Result:** ~30–50% reduction in redundant topics, clean hierarchical structure.

### 2. Higher-Order Quiz Engine
Forces **Analyze-level** questions (not just Recall). Uses knowledge graph edges in prompts so questions compare/contrast topics or predict consequences.

**Cognitive mix**:
- Understanding (30%): Explain formulas, reasoning
- Application (40%): Solve concrete problems
- Analyze (30%): Compare concepts, use Graph edges

### 3. Degradation & Meme Tracking (v1.0 NEW!)
**Tracks knowledge decay** with S/A/B/C/D tiers and animated meme cards:
- **S (Buff Doge)** — mastery maintained
- **A (Bright Campfire)** — strong understanding
- **B (Dying Embers)** — needs review soon
- **C (Smoke)** — mostly forgotten
- **D (Dark)** — relearn required

HomeScreen + ProfileScreen show animated stats, badges, and degradation trends with Comic-style memes.

### 4. GraphRAG Query System
Query the knowledge graph with natural language via Cognee orchestration. Use the Android app or API directly.

### 5. Multi-Model Rate Limiting & Quota Relief
- `AsyncRateLimiter` enforces RPM per model (12 RPM for Gemma, 60 for OpenAI embeddings)
- `quota_relief.py`: embedding model pool with automatic 429 failover
- Switches between Gemini and OpenAI embeddings seamlessly
- Patches litellm globally to respect rate limits

### 6. Streamlit Test UI (6-page wizard)
`http://localhost:8501` — Full testing pipeline:
1. **Upload** document → extract graph
2. **Topics** — review generated knowledge nodes
3. **Quiz** — take assessment, see Bloom level per question
4. **Result** — skill level updates, degradation tier changes
5. **Learning Path** — personalized recommendation with locked topics ⚠️
6. **Knowledge Graph** ⭐ — visualize the full graph (Kuzu)
7. **GraphRAG** ⭐ — natural language Q&A over the graph

---

## 🔧 Configuration

Create `backend/.env` from `.env.example` and configure:

```bash
# ── LLM & Embedding ─────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key          # optional
OPENROUTER_MODEL=google/gemma-4-26b-a4b-it
GEMINI_FALLBACK_MODEL=gemma-4-31b-it
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_PROVIDER_ORDER=nvidia,groq,together

# GraphRAG LLM (用于问答和Cypher生成)
GRAPHRAG_QA_MODEL=models/gemini-2.0-flash
GRAPHRAG_CYPHER_MODEL=models/gemini-2.0-flash

# ── Graph Database ───────────────────────────────────────
# Kuzu (default embedded graph DB)
GRAPH_DATABASE_PROVIDER=kuzu

# Cognee (knowledge graph orchestration layer)
GRAPH_PROVIDER=cognee
COGNEE_API_KEY=your_cognee_key                      # optional (if using hosted)
SYSTEM_ROOT_DIRECTORY=.cognee_system
DATA_ROOT_DIRECTORY=.cognee_data

# Neo4j (optional, for legacy/debug)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# ── JWT Auth ─────────────────────────────────────────────
JWT_SECRET_KEY=your_super_secret_key_change_this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ── File Upload ──────────────────────────────────────────
MAX_FILE_SIZE_MB=100
```

**Android `local.properties`:**
```properties
sdk.dir=/c/Users/Manh/AppData/Local/Android/sdk
gemini.api.key=AIzaSy...
```

---

## 🚀 Setup Guide

### Backend (Local)
```bash
cd backend

# Create venv + install
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Configure .env (see above)
cp .env.example .env
# Edit .env with your keys

# (Optional) Run Neo4j for debug/legacy
docker run -d --name studentlearn-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH='neo4j/your_password' \
  neo4j:5-community

# Run backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 7000

# OpenAPI docs: http://localhost:7000/docs
# ReDoc: http://localhost:7000/redoc
```

### Streamlit UI (removed)

### Android App
```bash
# From project root
./setup.sh sdk      # Auto-detect/configure SDK
./setup.sh build    # Build debug APK
./setup.sh emulator # Create + run Android Virtual Device
./setup.sh install  # Install APK on running emulator/device
```

Or use Android Studio:
- Open project in `./app/`
- Sync Gradle (wrapper: `gradle/wrapper/gradle-wrapper.properties`)
- Set `local.properties` with `sdk.dir=/path/to/android/sdk`
- Add `gemini.api.key=YOUR_KEY` to `local.properties`
- Run `app` module on emulator/device

---

## 🧪 Testing

### Android Unit Tests
```bash
./gradlew testDebugUnitTest
```
**Coverage:** 77 tests across:
- `DegradationCalculatorTest` — tier S→A→B→C→D decay math
- `DegradationTierTest` — color/icon/emoji mappings
- `SkillLevelCalculatorTest` — FR-13 scoring (0-1→L1, 2-3→L2, 4-5→L3)
- `SelfRatingMapperTest` — FR-22 self-rating mapping
- `PrerequisiteCheckerTest` — CON-D03 transitive prerequisite
- `TextChunkerTest` — CON-S02 chunking ≤3000 chars
- `QuizParserTest` — CON-A05 validation

### Backend Health & Diagnostics
```bash
# Health check
curl http://localhost:7000/api/v1/health

# Diagnostic (requires JWT)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:7000/api/v1/health/diagnostic

# Download OpenAPI spec
curl http://localhost:7000/api/v1/openapi.yaml -o openapi.yaml
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| SDK not found | Check `local.properties` with forward slashes (`/`), run `./setup.sh sdk` |
| Kuzu import error | `pip install kuzu` (default graph DB, replaces Neo4j local dependency) |
| Neo4j auth failed (legacy) | Match `NEO4J_PASSWORD` in `.env` vs Docker `NEO4J_AUTH` |
| 429 Rate Limit (Gemini) | Wait 24h or switch to OpenRouter provider; `quota_relief` auto-fails over to OpenAI embeddings |
| Backend 500 error | Check Neo4j/Kuzu connection; inspect logs via `/api/v1/health/diagnostic` |
| APK install failed | Ensure emulator is running (`adb devices`), use `./setup.sh emulator` |
| Room DB migration | Database version bumped automatically; clear app data on major schema changes |
| GraphRAG timeout | Increase `GRAPHRAG_QA_TIMEOUT` in `.env`, check graph connection status |
| Embedding dimensions error (V2) | Using `gemini/text-embedding-004` fixed 768D — no `dimensions` kwarg allowed (patched in `cognee_engine.py`) |

---

## 📊 Project Status

✅ **Phase 1–8 COMPLETE** (2026-04-20)  
✅ **v1.0 Overhaul Complete** (2026-05-10) — Commit: `78ef258`

| Phase | Agent | Status | Highlights |
|-------|-------|--------|------------|
| D | Design | ✅ | Wireframes, component library, accessibility, offline states |
| 1 | Architect | ✅ | Clean Architecture, Hilt DI, EmberComponents theme |
| 2 | Knowledge Graph | ✅ | Room entities, DAOs, Kuzu+Cognee v2, transitive-prereq CTE |
| 3 | Document Ingestion | ✅ | Gemini extractor, semantic aggregation (4-phase pipeline) |
| 4 | Assessment | ✅ | Bloom's quiz generator, skill level calculator, persistence |
| 5 | Recommendation | ✅ | Priority engine (≤2s), locked-topic blocking |
| 6 | Session Logger | ✅ | Self-rating mapper, degradation calculator (S/A/B/C/D) |
| 7 | UI/UX | ✅ | 7 screens, BottomNavigation, Home+Profile, meme widgets |
| 8 | Testing | ✅ | 77 unit tests, integration PASSED |

**v1.0 Overhaul Features (commit 78ef258):**
- Android UI rebrand: **EmberComponents** theme + BottomNavigationBar (4-tab)
- New screens: **HomeScreen** (stats, badges, degradation meme), **ProfileScreen** (analytics)
- **Degradation system** with 5-tier meme cards (S/A/B/C/D) + `DegradationCalculator` use case
- Backend refresh: `rate_limiter`, `quota_relief` (multi-model embedding pool), `diagnostic`, `task_manager`
- Graph DB upgrade: **Kuzu** (embedded) + Cognee 1.0 (replaces pure Neo4j approach)
- API alignment: `StudentLearnApi.kt` Retrofit interface (OpenAPI spec at `/api/v1/openapi.yaml`)
- Auth: `AuthClient.kt` with JWT `TokenManager` + `AuthInterceptor` for Bearer tokens
- Deploy: `render.yaml` configured, backend deployed to Render cloud

---

## 🔐 API Endpoints (v1)

```
GET    /api/v1/health                    # Service health + graph connection status
GET    /api/v1/health/diagnostic         # Full diagnostic ( auth required )
GET    /api/v1/openapi.yaml              # OpenAPI spec download

POST   /api/v1/auth/login                # JWT login
POST   /api/v1/auth/refresh              # Refresh token

POST   /api/v1/documents/upload          # Upload PDF/DOCX/TXT → extract graph
GET    /api/v1/documents/{id}            # Get document metadata
GET    /api/v1/documents/{id}/topics     # List topics for a document

POST   /api/v1/quiz/generate             # Generate quiz for a topic
POST   /api/v1/quiz/submit               # Submit answers → skill level update
GET    /api/v1/quiz/history/{topic_id}   # Quiz history for a topic

GET    /api/v1/learning_path/recommend   # Top N recommended topics
PUT    /api/v1/user_progress/self_rate   # Update self-rating → degradation calc

POST   /api/v1/graph_rag/query           # Natural language GraphRAG query
GET    /api/v1/graph_rag/topics          # List all topics (graph nodes)
GET    /api/v1/graph_rag/edges           # List all edges (graph relationships)
```

Full interactive docs: **http://localhost:7000/docs**

---

## 🎨 Color System (FR-06)

| Level | Color | Degradation Tier | Icon/Meme |
|-------|-------|------------------|-----------|
| 0 (Locked) | `#9CA3AF` Gray | D (Dark) | 🔒 |
| 1 (Beginner) | `#EF4444` Red | C (Smoke) | 🌱 |
| 2 (Intermediate) | `#F59E0B` Yellow | B (Dying Embers) | 🔥 |
| 3 (Mastered) | `#10B981` Green | A (Bright Campfire) | ⭐ |
| Mastery (S) | `#8B5CF6` Purple | S (Buff Doge) | 🐕 |

Used in: `TopicCard`, `DegradationMemeCard`, Progress charts, Knowledge Map.

---

## 📜 License

Educational project — see `LICENSE` (if added).

---

## 🙏 Acknowledgements

Built with Claude Code (Anthropic), Gemini API, Cognee, Kuzu, FastAPI, Jetpack Compose.

Questions? Open an issue or check `docs/` for detailed design docs.
