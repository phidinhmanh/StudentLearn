# Test Commands - KnowledgeMap Project

## Quick Setup (One-time)

```bash
# 1. Install Python dependencies for backend
cd backend
pip install -r requirements.txt

# 2. Verify .env has Gemini API key
# Check backend/.env file - should have: GEMINI_API_KEY=your_key_here
```

## IMPORTANT: Gemini API Quota

Gemini free tier has daily limits. If you get "429 Too Many Requests" or empty results:
- Wait 24 hours for quota reset
- Or upgrade to paid plan at https://ai.dev/rate-limit
- Check quota: https://ai.google.dev/rate-limit

## Backend Commands (Run First)

```bash
# 1. Navigate to backend
cd backend

# 2. Run backend server (port 8000 or 8001 if 8000 busy)
uvicorn cognee_service.main:app --host 0.0.0.0 --port 8000 --reload

# Or if port 8000 is busy:
uvicorn cognee_service.main:app --host 0.0.0.0 --port 8001 --reload
```

## API Testing Commands

```bash
# 1. Health check
curl http://localhost:8000/api/v1/health

# 2. Test knowledge graph extraction (requires Gemini quota)
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d @test_request.json

# 3. Test RAG query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "ham so bac 2", "top_k": 5}'
```

## Expected Results (when Gemini quota available)

- Health: `{"status": "ok", "version": "1.0.0", "gemini_configured": true}`
- Ingest: Returns nodes/edges or empty if quota exceeded

## Android Commands

```bash
# 1. Navigate to project root
cd ..

# 2. Build debug APK
./gradlew assembleDebug

# 3. Clean build
./gradlew clean assembleDebug

# 4. Run tests
./gradlew test

# 5. Run connected tests (requires emulator/device)
./gradlew connectedAndroidTest
```

## Full Test Flow

```bash
# Step 1: Start backend
cd backend
uvicorn cognee_service.main:app --reload

# Step 2: In another terminal - Test API
curl http://localhost:8000/api/v1/health

# Step 3: Build Android
cd ..
./gradlew assembleDebug

# Step 4: Install on emulator
adb install -r app/build/outputs/apk/debug/app-debug.apk

# Step 5: Start emulator
emulator -avd <avd_name>  # e.g., emulator -avd Pixel_6_API_33

# Step 6: Launch app
adb shell am start -n com.knowledgemap.app/.MainActivity
```

## Feature Testing Checklist

- [ ] **Onboarding Screen**: First launch shows onboarding flow
- [ ] **Knowledge Map**: Main screen displays topic nodes correctly
- [ ] **Navigation**: "Bat dau hoc" button navigates to Assessment
- [ ] **Quiz**: Questions load and display correctly
- [ ] **Recommendation**: After quiz, recommendations appear
- [ ] **Offline Mode**: App works without internet (basic features)
- [ ] **Session Logger**: Study sessions are recorded

## Troubleshooting

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process on port 8000
taskkill /PID <pid> /F

# Gemini API Quota exceeded (HTTP 429)?
# - Free tier: Wait 24 hours for reset
# - Or upgrade at: https://ai.google.dev/rate-limit
# - Check quota status: https://ai.dev/rate-limit

# Clear Android build cache
./gradlew clean
./gradlew --stop

# Re-sync Gradle
./gradlew --refresh-dependencies
```

## API Response Examples

### Health Response
```json
{"status": "ok", "version": "1.0.0", "gemini_configured": true}
```

### Ingest Response
```json
{
  "success": true,
  "nodes": [
    {"id": "ham_so_bac_2", "name": "Ham so bac 2", "desc": "...", "difficulty": 2}
  ],
  "edges": [
    {"from_id": "ham_so_bac_1", "to_id": "ham_so_bac_2", "relation": "prerequisite"}
  ],
  "chunks_processed": 3
}
```

## Project Structure

```
StudentLearn/
├── app/                          # Android app
│   ├── src/main/
│   │   ├── java/com/knowledgemap/app/
│   │   │   ├── data/             # Data layer
│   │   │   │   ├── local/        # Room database
│   │   │   │   ├── remote/       # API client
│   │   │   │   └── repository/   # Repositories
│   │   │   ├── di/               # Dependency injection
│   │   │   ├── domain/           # Business logic
│   │   │   │   └── usecase/      # Use cases
│   │   │   └── ui/               # UI layer
│   │   │       ├── screen/       # Screens
│   │   │       ├── components/   # Reusable components
│   │   │       └── navigation/   # Navigation
│   │   └── res/                  # Resources
│   └── build.gradle.kts
├── backend/                      # Python backend
│   ├── cognee_service/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── models.py            # Pydantic models
│   │   ├── routers/             # API endpoints
│   │   └── services/            # Business logic
│   ├── data/                    # Data storage
│   │   ├── documents/           # Input documents
│   │   └── graphs/              # Extracted graphs
│   └── requirements.txt
├── docs/                         # Documentation
├── SRS.md                        # Requirements spec
└── CLAUDE.md                     # Project instructions
```