# KnowledgeMap Learning App

Android app giúp học sinh THPT tự xác định lỗ hổng kiến thức và nhận gợi ý lộ trình học cá nhân hóa.

---

## Quick Start

### Interactive Menu
```bash
chmod +x setup.sh
./setup.sh
```

Hiển thị menu với 10 options:

| # | Option | Mô tả |
|---|--------|-------|
| 1 | Setup Android SDK | Tìm SDK, generate `local.properties` |
| 2 | Build Debug APK | `./gradlew assembleDebug` |
| 3 | Install Emulator | Tải emulator + system image, tạo AVD |
| 4 | Start Emulator | Khởi động emulator + cài APK |
| 5 | Build + Install | Build APK rồi cài lên device/emulator |
| 6 | Setup Backend | Tạo venv, pip install dependencies |
| 7 | Run Backend Server | Start uvicorn trên port 8000 |
| 8 | View Logcat (live) | Xem log trực tiếp từ app |
| 9 | Crash Log | Dump crash log + lưu vào file |
| 10 | Full Setup | Chạy 1 + 2 + 6 cùng lúc |

### CLI (non-interactive)
```bash
./setup.sh sdk        # Setup SDK
./setup.sh build      # Build debug APK
./setup.sh emu        # Install emulator
./setup.sh run-emu    # Start emulator
./setup.sh install    # Build + install on device
./setup.sh backend    # Setup Python backend
./setup.sh serve      # Run backend server
./setup.sh logcat     # View live logcat
./setup.sh crash      # Dump crash log to file
./setup.sh all        # Full setup
```

Sau khi chạy, chỉnh API key:
1. `local.properties` → `gemini.api.key=YOUR_KEY`
2. `backend/.env` → `GEMINI_API_KEY=YOUR_KEY`

---

## Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| Java JDK | 17+ | [Adoptium](https://adoptium.net) |
| Python | 3.9+ | [python.org](https://python.org) |
| Android SDK | 34 | [Android Studio](https://developer.android.com/studio) (recommended) |
| Gemini API Key | - | [AI Studio](https://aistudio.google.com/apikey) |

---

## Manual Setup

Nếu không dùng `setup.sh`, thiết lập thủ công theo OS:

### macOS

```bash
# SDK path mặc định (Android Studio tự cài)
# local.properties:
sdk.dir=/Users/YOUR_USER/Library/Android/sdk
gemini.api.key=YOUR_API_KEY_HERE

# Install SDK components (nếu cần)
sdkmanager "platforms;android-34" "build-tools;34.0.0" "platform-tools"

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Linux

```bash
# SDK path mặc định
# local.properties:
sdk.dir=/home/YOUR_USER/Android/Sdk
gemini.api.key=YOUR_API_KEY_HERE

# Install SDK components
sdkmanager "platforms;android-34" "build-tools;34.0.0" "platform-tools"

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
# SDK path mặc định (Git Bash)
# local.properties:
sdk.dir=D:/Android/Sdk
gemini.api.key=YOUR_API_KEY_HERE

# Install SDK components (thêm .bat)
sdkmanager.bat "platforms;android-34" "build-tools;34.0.0" "platform-tools"

# Backend (Git Bash)
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

> **Windows note:** Dùng `.bat` cho `sdkmanager`, `avdmanager`. Dùng `.exe` cho `adb`, `emulator`.

---

## Install Android SDK (Command-Line Only)

Nếu chưa có Android SDK và không dùng Android Studio:

### macOS / Linux

```bash
# Tạo thư mục SDK
mkdir -p ~/Android/Sdk    # Linux
mkdir -p ~/Library/Android/sdk  # macOS

# Download command-line tools
# macOS
curl -L -o /tmp/cmdline-tools.zip \
  "https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip"
# Linux
curl -L -o /tmp/cmdline-tools.zip \
  "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"

# Giải nén
SDK_DIR=~/Android/Sdk  # hoặc ~/Library/Android/sdk (macOS)
unzip -q /tmp/cmdline-tools.zip -d $SDK_DIR
mv $SDK_DIR/cmdline-tools $SDK_DIR/cmdline-tools-temp
mkdir -p $SDK_DIR/cmdline-tools
mv $SDK_DIR/cmdline-tools-temp $SDK_DIR/cmdline-tools/latest

# Accept licenses & install
$SDK_DIR/cmdline-tools/latest/bin/sdkmanager --licenses
$SDK_DIR/cmdline-tools/latest/bin/sdkmanager \
  "platforms;android-34" "build-tools;34.0.0" "platform-tools"
```

### Windows

```powershell
# Tạo thư mục SDK
mkdir D:\Android\Sdk

# Download command-line tools (PowerShell)
Invoke-WebRequest -Uri `
  "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip" `
  -OutFile D:\cmdline-tools.zip
Expand-Archive D:\cmdline-tools.zip -DestinationPath D:\Android\Sdk
Rename-Item D:\Android\Sdk\cmdline-tools cmdline-tools-temp
mkdir D:\Android\Sdk\cmdline-tools
Move-Item D:\Android\Sdk\cmdline-tools-temp D:\Android\Sdk\cmdline-tools\latest

# Accept licenses & install
D:\Android\Sdk\cmdline-tools\latest\bin\sdkmanager.bat --licenses
D:\Android\Sdk\cmdline-tools\latest\bin\sdkmanager.bat `
  "platforms;android-34" "build-tools;34.0.0" "platform-tools"
```

---

## Emulator Setup (Optional)

### macOS / Linux

```bash
SDK=~/Android/Sdk  # hoặc ~/Library/Android/sdk (macOS)

$SDK/cmdline-tools/latest/bin/sdkmanager \
  "emulator" "system-images;android-34;google_apis;x86_64"

$SDK/cmdline-tools/latest/bin/avdmanager create avd \
  -n "KnowledgeMapDevice" -k "system-images;android-34;google_apis;x86_64"

$SDK/emulator/emulator -avd KnowledgeMapDevice &
sleep 30
./gradlew installDebug
```

### Windows

```bash
SDK=/d/Android/Sdk

$SDK/cmdline-tools/latest/bin/sdkmanager.bat \
  "emulator" "system-images;android-34;google_apis;x86_64"

$SDK/cmdline-tools/latest/bin/avdmanager.bat create avd \
  -n "KnowledgeMapDevice" -k "system-images;android-34;google_apis;x86_64"

$SDK/emulator/emulator.exe -avd KnowledgeMapDevice &
sleep 30
./gradlew installDebug
```

### Tắt Emulator

| OS | Command |
|----|---------|
| macOS / Linux | `adb emu kill` |
| Windows | `adb.exe emu kill` |

---

## Common Commands

```bash
# Build
./gradlew assembleDebug          # Debug APK
./gradlew assembleRelease        # Release APK
./gradlew clean                  # Clean build

# Test
./gradlew test                   # Unit tests
./gradlew connectedAndroidTest   # Instrumented tests

# Backend
cd backend
uvicorn cognee_service.main:app --host 0.0.0.0 --port 8000 --reload

# API Test
curl http://localhost:8000/api/v1/health
```

---

## Project Structure

```
app/src/main/java/com/knowledgemap/app/
├── data/local/     # Room database (entities, DAOs)
├── data/remote/    # Gemini API client
├── data/repository/# Repository implementations
├── data/utils/     # Utilities
├── di/             # Hilt modules
├── domain/model/   # Domain models
├── domain/usecase/ # Use cases
└── ui/             # Compose UI (screens, navigation, theme)

backend/cognee_service/
├── main.py         # FastAPI app
├── config.py       # Configuration
├── routers/        # API endpoints
└── services/       # Business logic
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "SDK location not found" | Check `local.properties` has correct path with forward slashes (`/` not `\`) |
| "Emulator not found" | List AVDs: `avdmanager list avd` (`.bat` on Windows) |
| "Activity not found" | Use full name: `com.knowledgemap.app/com.knowledgemap.app.ui.MainActivity` |
| Gemini 429 error | Free tier limit (~60 req/day). Wait 24h or upgrade at https://ai.google.dev/rate-limit |
| Python not found | Install Python 3.9+ from https://python.org |

## Debugging

### View Live Logs (Option 8)
```bash
./setup.sh logcat
```
Xem log trực tiếp từ app trên thiết bị/emulator. Ctrl+C để dừng.

### Crash Log (Option 9)
```bash
./setup.sh crash
```
Dump crash log từ logcat buffer, lưu vào file `logs/crash_YYYYMMDD_HHMMSS.log`. File bao gồm:
- FATAL EXCEPTION từ AndroidRuntime
- App logs (errors + warnings)
- System crash buffer
- Device info (model, Android version, SDK)

**Cách sử dụng:**
1. Reproduce crash trên app
2. Chạy `./setup.sh crash`
3. Share file `logs/crash_*.log` khi báo lỗi

---

## Development Phases

| Phase | Status |
|-------|--------|
| D: Design Agent | Complete |
| 1: Architecture Setup | Complete |
| 2: Knowledge Graph | Complete |
| 3: Document Ingestion | Complete |
| 4: Assessment | Complete |
| 5: Recommendation Engine | Complete |
| 6: Session Logger | Complete |
| 7: UI/UX | Complete |
| 8: Testing | Complete |
