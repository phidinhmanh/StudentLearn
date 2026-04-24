# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Android app giúp học sinh THPT tự xác định lỗ hổng kiến thức và nhận gợi ý lộ trình học cá nhân hóa.

- **Frontend:** Android (Kotlin + Jetpack Compose)
- **Backend:** Python FastAPI (FastAPI + LangChain)
- **AI Engine:** Groq API — `llama-3.3-70b-versatile` (128k context, fast inference)
- **Database:** Neo4j (Docker, local), Room (Android local-first)

## Architecture & Patterns

### Android App (MVVM + Clean Architecture)
- **`ui/`**: Jetpack Compose screens. State-hoisted components observing ViewModels via `StateFlow`.
- **`domain/`**: Pure Kotlin logic. UseCases orchestrate business logic (e.g., `AssessmentUseCase`, `RecommendationEngine`).
- **`data/`**: 
    - **local/**: Room DB, entities (`TopicNodeEntity`, `TopicEdgeEntity`), and DAOs with CTE queries for transitive prerequisites.
    - **remote/**: API clients for Gemini (direct) and FastAPI Backend.
    - **repository/**: Aggregates local/remote data using the Repository pattern.
- **`di/`**: Hilt modules for dependency injection.

### Python Backend (FastAPI)
- **`app/`**: Core API logic (FastAPI + LangChain)
- **`app/routers/`**: API endpoints (Health, Ingest, Quiz, Path)
- **`app/services/`**: Neo4j operations and LLM logic
- **`app/test_ui/`**: Streamlit test UI (runs on `:8501`)

### Knowledge Graph Schema
- **Nodes**: `topic_node` with `skill_level` ∈ {0, 1, 2, 3} (0=Xám/Locked, 1=Đỏ, 2=Vàng, 3=Xanh).
- **Edges**: `topic_edge` with relations: `prerequisite`, `sequenceOf`, `relatedTo`.
- **Constraint**: Topics are "locked" if transitive prerequisites have `skill_level` < 2.

## Development Commands

### Android (Root Directory)
- **Build**: `./gradlew.bat assembleDebug`
- **Clean**: `./gradlew.bat clean`
- **Unit Tests**: `./gradlew.bat test`
- **Single Unit Test**: `./gradlew.bat testDebugUnitTest --tests "com.knowledgemap.app.domain.usecase.RecommendationEngineTest"`
- **Instrumented Tests**: `./gradlew.bat connectedAndroidTest`
- **Install APK**: `adb install -r app/build/outputs/apk/debug/app-debug.apk`

### Python Backend (`/backend`)
- **Setup Venv**: `python -m venv .venv`
- **Activate Venv**: `source .venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (Unix)
- **Install Deps**: `pip install -r requirements.txt`
- **Run Server**: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Health Check**: `curl http://localhost:8000/api/v1/health`

## Key Logic & Constraints
- **Scoring (FR-13)**: 0-1 correct → L1, 2-3 correct → L2, 4-5 correct → L3.
- **Self-Rating (FR-22)**: Hiểu rõ → +1 skill, Chưa hiểu → -1 skill, Cần ôn tập → 0 change.
- **Recommendation (FR-17)**: Priority order: 1. Prerequisite gaps, 2. Ready to learn (all prereqs met), 3. Review (L1/L2 topics).
- **Performance**: Recommendation engine must run in < 2s offline.
- **Data Safety**: Never delete assessment history automatically (FR-24).
- **Seeding**: Initial graph loaded from `assets/toan10_graph.json` via `DatabaseModule` on first launch.
