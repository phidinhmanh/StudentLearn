@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: KnowledgeMap Learning App - Setup Script (Windows)
:: Usage: setup.bat [sdk|build|emu|run-emu|install|backend|serve|logcat|crash|all]

:: --- Colors (ANSI, Windows 10+) ---
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "CYAN=%ESC%[96m"
set "NC=%ESC%[0m"

:: --- Verify project root ---
if not exist "gradlew" (
    echo ERROR: Run this script from the project root directory
    exit /b 1
)
if not exist "gradlew.bat" (
    echo ERROR: Run this script from the project root directory
    exit /b 1
)

:: --- Resolve SDK path ---
:resolve_sdk
if defined ANDROID_HOME (
    set "SDK_PATH=%ANDROID_HOME%"
    goto :sdk_done
)
if defined ANDROID_SDK_ROOT (
    set "SDK_PATH=%ANDROID_SDK_ROOT%"
    goto :sdk_done
)
:: Default Windows paths
if exist "D:\Android\Sdk" (
    set "SDK_PATH=D:\Android\Sdk"
    goto :sdk_done
)
if exist "C:\Android\Sdk" (
    set "SDK_PATH=C:\Android\Sdk"
    goto :sdk_done
)
if exist "%LOCALAPPDATA%\Android\Sdk" (
    set "SDK_PATH=%LOCALAPPDATA%\Android\Sdk"
    goto :sdk_done
)
set "SDK_PATH="
:sdk_done

:: --- Command line args ---
if "%~1"=="" goto :menu
call :do_%1 2>nul
if errorlevel 1 (
    echo Usage: setup.bat [sdk^|build^|emu^|run-emu^|install^|backend^|serve^|logcat^|crash^|all]
)
exit /b 0

:: ============================================================
::  ACTIONS
:: ============================================================

:do_sdk
echo.
echo %CYAN%=== Android SDK Setup ===%NC%
echo SDK path: %SDK_PATH%

if "%SDK_PATH%"=="" (
    echo %RED%SDK not found!%NC%
    echo.
    echo Install options:
    echo   1. Android Studio ^(recommended^): https://developer.android.com/studio
    echo   2. Command-line tools: https://developer.android.com/studio#command-line-tools-only
    echo   3. Set ANDROID_HOME environment variable
    exit /b 1
)

if not exist "%SDK_PATH%" (
    echo %RED%SDK not found at: %SDK_PATH%%NC%
    echo Install Android Studio or set ANDROID_HOME
    exit /b 1
)

:: Check subdirectories
set "SDK_OK=1"
if not exist "%SDK_PATH%\platforms" set "SDK_OK=0"
if not exist "%SDK_PATH%\build-tools" set "SDK_OK=0"
if not exist "%SDK_PATH%\platform-tools" set "SDK_OK=0"

if "!SDK_OK!"=="0" (
    echo %YELLOW%SDK incomplete. Installing missing components...%NC%
    set "SMGR=%SDK_PATH%\cmdline-tools\latest\bin\sdkmanager.bat"
    if exist "!SMGR!" (
        echo y | "!SMGR!" "platforms;android-34" "build-tools;34.0.0" "platform-tools"
    ) else (
        echo sdkmanager not found. Install via Android Studio SDK Manager.
    )
) else (
    echo %GREEN%SDK OK%NC% ^(platforms, build-tools, platform-tools^)
)

:: Generate local.properties
:: Use Windows backslash path
set "SDK_WIN=%SDK_PATH%"
if exist "local.properties" (
    findstr /C:"gemini.api.key=" local.properties >nul 2>&1
    if !errorlevel!==0 (
        for /f "tokens=1,* delims==" %%a in ('findstr "^gemini.api.key=" local.properties') do set "EXISTING_KEY=%%b"
    )
    if defined EXISTING_KEY if not "!EXISTING_KEY!"=="YOUR_API_KEY_HERE" (
        powershell -Command "(Get-Content local.properties) -replace '^sdk\.dir=.*', 'sdk.dir=%SDK_WIN%' | Set-Content local.properties"
        echo %GREEN%Updated local.properties%NC% ^(kept existing API key^)
    ) else (
        > local.properties (
            echo sdk.dir=%SDK_WIN%
            echo gemini.api.key=YOUR_API_KEY_HERE
        )
        echo %GREEN%Generated local.properties%NC% ^(add your API key!^)
    )
) else (
    > local.properties (
        echo sdk.dir=%SDK_WIN%
        echo gemini.api.key=YOUR_API_KEY_HERE
    )
    echo %GREEN%Generated local.properties%NC% ^(add your API key!^)
)
exit /b 0

:do_build
echo.
echo %CYAN%=== Build Debug APK ===%NC%
call gradlew.bat assembleDebug
if errorlevel 1 (
    echo %RED%Build FAILED%NC%
    exit /b 1
)
echo %GREEN%Build successful!%NC%
echo APK: app\build\outputs\apk\debug\app-debug.apk
exit /b 0

:do_emu
echo.
echo %CYAN%=== Install Emulator + System Image ===%NC%
if "%SDK_PATH%"=="" (
    echo %RED%SDK not found. Run option 1 first.%NC%
    exit /b 1
)
set "SMGR=%SDK_PATH%\cmdline-tools\latest\bin\sdkmanager.bat"
if not exist "!SMGR!" (
    echo %RED%sdkmanager not found at: !SMGR!%NC%
    echo Install Android SDK first ^(option 1^)
    exit /b 1
)

echo Installing emulator and system image ^(android-34, google_apis, x86_64^)...
echo y | "!SMGR!" "emulator" "system-images;android-34;google_apis;x86_64"

set "AVDMGR=%SDK_PATH%\cmdline-tools\latest\bin\avdmanager.bat"
echo Creating AVD 'KnowledgeMapDevice'...
echo no | "!AVDMGR!" create avd -n "KnowledgeMapDevice" -k "system-images;android-34;google_apis;x86_64" 2>nul
echo %GREEN%Emulator ready!%NC% AVD: KnowledgeMapDevice
exit /b 0

:do_run-emu
echo.
echo %CYAN%=== Run Emulator ===%NC%
if "%SDK_PATH%"=="" (
    echo %RED%SDK not found. Run option 1 first.%NC%
    exit /b 1
)
set "EMU=%SDK_PATH%\emulator\emulator.exe"
if not exist "!EMU!" (
    echo %RED%Emulator not found. Install it first ^(option 3^)%NC%
    exit /b 1
)

echo Starting emulator...
start "" "!EMU!" -avd KnowledgeMapDevice

set "ADB=%SDK_PATH%\platform-tools\adb.exe"
echo Waiting for emulator to boot...
"!ADB!" wait-for-device
timeout /t 10 /nobreak >nul
echo %GREEN%Emulator running!%NC%

if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo Installing APK...
    "!ADB!" install -r app\build\outputs\apk\debug\app-debug.apk
    echo %GREEN%App installed!%NC% Launch with:
    echo   !ADB! shell am start -n com.knowledgemap.app/com.knowledgemap.app.ui.MainActivity
) else (
    echo %YELLOW%APK not found. Build first ^(option 2^) then install.%NC%
)
exit /b 0

:do_install
echo.
echo %CYAN%=== Build + Install on Device/Emulator ===%NC%
call :do_build
if errorlevel 1 exit /b 1

set "ADB=%SDK_PATH%\platform-tools\adb.exe"
if not exist "!ADB!" (
    echo %RED%adb not found. Run option 1 first.%NC%
    exit /b 1
)

:: Check for devices
set "HAS_DEVICE=0"
for /f %%i in ('"!ADB!" devices 2^>nul ^| find /c "device"') do set /a HAS_DEVICE=%%i
if !HAS_DEVICE! lss 2 (
    echo %YELLOW%No device/emulator running.%NC%
    echo Options:
    echo   1. Start emulator first ^(option 4^)
    echo   2. Connect physical device via USB ^(with USB debugging enabled^)
    echo   3. Install APK later manually
    set /p "START_EMU=Start emulator now? (y/N): "
    if /i "!START_EMU!"=="y" (
        call :do_run-emu
    ) else (
        echo APK ready at: app\build\outputs\apk\debug\app-debug.apk
        exit /b 0
    )
)

echo Installing APK on device...
"!ADB!" install -r app\build\outputs\apk\debug\app-debug.apk
echo %GREEN%App installed!%NC% Launching...
"!ADB!" shell am start -n "com.knowledgemap.app/com.knowledgemap.app.ui.MainActivity"
exit /b 0

:do_backend
echo.
echo %CYAN%=== Python Backend Setup ===%NC%

where python >nul 2>&1
if errorlevel 1 (
    echo %RED%Python not found. Install Python 3.9+: https://python.org%NC%
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do echo Using: %%i

if not exist "backend\.venv" (
    echo Creating virtual environment...
    python -m venv backend\.venv
) else (
    echo Virtual environment already exists, reusing...
)

call backend\.venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r backend\requirements.txt -q
echo %GREEN%Backend setup complete.%NC%
exit /b 0

:do_serve
echo.
echo %CYAN%=== Run Python Backend Server ===%NC%

if exist "backend\.venv\Scripts\activate.bat" (
    call backend\.venv\Scripts\activate.bat
) else (
    echo %YELLOW%Virtual environment not found. Running setup first...%NC%
    call :do_backend
    if errorlevel 1 exit /b 1
)

if not exist "backend\.env" (
    echo %RED%backend\.env not found!%NC%
    exit /b 1
)

:: Check API key
set "GEMINI_KEY="
for /f "tokens=1,* delims==" %%a in ('findstr "^GEMINI_API_KEY=" backend\.env') do set "GEMINI_KEY=%%b"
if "%GEMINI_KEY%"=="" (
    echo %YELLOW%WARNING: Gemini API key not configured in backend\.env%NC%
    echo The server will start but AI features won't work.
    set /p "CONT=Continue? (y/N): "
    if /i not "!CONT!"=="y" exit /b 0
)
if "!GEMINI_KEY!"=="YOUR_API_KEY_HERE" (
    echo %YELLOW%WARNING: Gemini API key not configured in backend\.env%NC%
    echo The server will start but AI features won't work.
    set /p "CONT=Continue? (y/N): "
    if /i not "!CONT!"=="y" exit /b 0
)

echo %GREEN%Starting backend server on http://localhost:8000%NC%
echo Press Ctrl+C to stop
echo.
cd backend
uvicorn cognee_service.main:app --host 0.0.0.0 --port 8000 --reload
exit /b 0

:do_logcat
echo.
echo %CYAN%=== View Logcat (Live) ===%NC%
set "ADB=%SDK_PATH%\platform-tools\adb.exe"
if not exist "!ADB!" (
    echo %RED%adb not found. Run option 1 first.%NC%
    exit /b 1
)

set "HAS_DEVICE=0"
for /f %%i in ('"!ADB!" devices 2^>nul ^| find /c "device"') do set /a HAS_DEVICE=%%i
if !HAS_DEVICE! lss 2 (
    echo %RED%No device/emulator connected.%NC%
    echo Start emulator ^(option 4^) or connect device via USB first.
    exit /b 1
)

echo Showing live logcat for KnowledgeMap app...
echo Filter: package=com.knowledgemap.app
echo Press Ctrl+C to stop
echo.
for /f "tokens=*" %%p in ('"!ADB!" shell pidof -s com.knowledgemap.app 2^>nul') do set "APP_PID=%%p"
if defined APP_PID (
    "!ADB!" logcat --pid=!APP_PID! -v time *:V
) else (
    "!ADB!" logcat -v time | findstr /i "knowledgemap AndroidRuntime FATAL CRASH"
)
exit /b 0

:do_crash
echo.
echo %CYAN%=== Crash Log ===%NC%
set "ADB=%SDK_PATH%\platform-tools\adb.exe"
if not exist "!ADB!" (
    echo %RED%adb not found. Run option 1 first.%NC%
    exit /b 1
)

set "HAS_DEVICE=0"
for /f %%i in ('"!ADB!" devices 2^>nul ^| find /c "device"') do set /a HAS_DEVICE=%%i
if !HAS_DEVICE! lss 2 (
    echo %RED%No device/emulator connected.%NC%
    echo Start emulator ^(option 4^) or connect device via USB first.
    exit /b 1
)

if not exist "logs" mkdir logs
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set "DATE_STR=%%a%%b%%c"
for /f "tokens=1-3 delims=:. " %%a in ('time /t') do set "TIME_STR=%%a%%b"
set "LOG_FILE=logs\crash_%DATE_STR%_%TIME_STR%.log"

echo Dumping crash logs...
echo.

echo === FATAL EXCEPTIONS === > "!LOG_FILE!"
"!ADB!" logcat -d -s "AndroidRuntime:E" -v threadtime >> "!LOG_FILE!" 2>nul

echo. >> "!LOG_FILE!"
echo === APP LOGS (Errors ^& Warnings) === >> "!LOG_FILE!"
for /f "tokens=*" %%p in ('"!ADB!" shell pidof -s com.knowledgemap.app 2^>nul') do set "APP_PID=%%p"
if defined APP_PID (
    "!ADB!" logcat -d --pid=!APP_PID! -v threadtime *:W >> "!LOG_FILE!" 2>nul
) else (
    "!ADB!" logcat -d -v threadtime | findstr /i "knowledgemap" >> "!LOG_FILE!" 2>nul
)

echo. >> "!LOG_FILE!"
echo === SYSTEM CRASH === >> "!LOG_FILE!"
"!ADB!" logcat -d -b crash -v threadtime >> "!LOG_FILE!" 2>nul

echo. >> "!LOG_FILE!"
echo === DEVICE INFO === >> "!LOG_FILE!"
for /f "tokens=*" %%m in ('"!ADB!" shell getprop ro.product.model 2^>nul') do echo Device: %%m >> "!LOG_FILE!"
for /f "tokens=*" %%v in ('"!ADB!" shell getprop ro.build.version.release 2^>nul') do echo Android: %%v >> "!LOG_FILE!"
for /f "tokens=*" %%s in ('"!ADB!" shell getprop ro.build.version.sdk 2^>nul') do echo SDK: %%s >> "!LOG_FILE!"
echo App PID: !APP_PID! >> "!LOG_FILE!"

:: Count crashes
set "CRASH_COUNT=0"
for /f %%c in ('findstr /c:"FATAL EXCEPTION" /c:"AndroidRuntime" "!LOG_FILE!" 2^>nul ^| find /c /v ""') do set /a CRASH_COUNT=%%c

if !CRASH_COUNT! gtr 0 (
    echo %RED%Found !CRASH_COUNT! crash^(es^)!%NC%
    echo.
    echo --- Last crash ---
    findstr /c:"FATAL EXCEPTION" "!LOG_FILE!" >nul && (
        for /f "tokens=1-20 delims=" %%l in ('type "!LOG_FILE!" ^| findstr /n "FATAL EXCEPTION"') do (
            echo %%l
        )
    )
) else (
    echo %GREEN%No crash found in current logcat buffer.%NC%
    echo Tip: Reproduce the crash then re-run this option.
)

echo.
echo Full log saved: %YELLOW%!LOG_FILE!%NC%
echo Share this file when reporting bugs.
exit /b 0

:do_all
echo.
echo %CYAN%=== Full Setup ===%NC%
call :do_sdk || echo.
call :do_backend || echo.
call :do_build
if errorlevel 1 exit /b 1
echo.
echo %GREEN%=== Full Setup Complete ===%NC%
echo.
echo Next steps:
echo   1. Edit local.properties - add Gemini API key
echo   2. Edit backend\.env - add Gemini API key
echo   3. Start backend: re-run setup.bat, option 7
echo   4. Install on phone: re-run setup.bat, option 5
exit /b 0

:: ============================================================
::  INTERACTIVE MENU
:: ============================================================

:menu
echo.
echo %CYAN%===========================================%NC%
echo %CYAN% KnowledgeMap Learning App - Setup Menu %NC%
echo %CYAN%===========================================%NC%
echo  OS: %GREEN%Windows%NC%
echo.
echo  %YELLOW%Android SDK:%NC%
echo   1. Setup Android SDK (local.properties)
echo   2. Build Debug APK
echo   3. Install Emulator + System Image
echo   4. Start Emulator
echo   5. Build + Install on Device/Emulator
echo.
echo  %YELLOW%Python Backend:%NC%
echo   6. Setup Backend (venv + pip install)
echo   7. Run Backend Server
echo.
echo  %YELLOW%Debug:%NC%
echo   8. View Logcat (live)
echo   9. Crash Log (dump + save to file)
echo.
echo  %YELLOW%Other:%NC%
echo   10. Full Setup (1 + 2 + 6)
echo   0. Exit
echo.

set /p "CHOICE= Choose option: "

if "%CHOICE%"=="1" call :do_sdk
if "%CHOICE%"=="2" call :do_build
if "%CHOICE%"=="3" call :do_emu
if "%CHOICE%"=="4" call :do_run-emu
if "%CHOICE%"=="5" call :do_install
if "%CHOICE%"=="6" call :do_backend
if "%CHOICE%"=="7" call :do_serve
if "%CHOICE%"=="8" call :do_logcat
if "%CHOICE%"=="9" call :do_crash
if "%CHOICE%"=="10" call :do_all
if "%CHOICE%"=="0" (
    echo Bye!
    exit /b 0
)

echo.
pause
goto :menu
