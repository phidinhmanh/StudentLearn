#!/usr/bin/env bash
# KnowledgeMap Learning App - Setup Script (macOS / Linux)
set -e

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- OS Detection ---
detect_os() {
	case "$(uname -s)" in
	Darwin*) echo "macos" ;;
	Linux*) echo "linux" ;;
	*) echo "unknown" ;;
	esac
}

OS=$(detect_os)

# --- SDK helpers ---
resolve_sdk_path() {
	if [ -n "$ANDROID_HOME" ]; then echo "$ANDROID_HOME"; return 0; fi
	if [ -n "$ANDROID_SDK_ROOT" ]; then echo "$ANDROID_SDK_ROOT"; return 0; fi
	case "$OS" in
	macos) echo "$HOME/Library/Android/sdk" ;;
	linux) echo "$HOME/Android/Sdk" ;;
	*) echo "" ;;
	esac
}

sdkmanager_bin() { echo "$1/cmdline-tools/latest/bin/sdkmanager"; }
avdmanager_bin() { echo "$1/cmdline-tools/latest/bin/avdmanager"; }
emulator_bin() { echo "$1/emulator/emulator"; }
adb_bin() { echo "$1/platform-tools/adb"; }

# --- Actions ---

do_sdk_setup() {
	echo -e "\n${CYAN}=== Android SDK Setup ===${NC}"
	local sdk_path
	sdk_path=$(resolve_sdk_path)
	echo "SDK path: $sdk_path"

	if [ ! -d "$sdk_path" ]; then
		echo -e "${RED}SDK not found at: $sdk_path${NC}"
		echo ""
		echo "Install options:"
		echo "  1. Android Studio (recommended): https://developer.android.com/studio"
		echo "  2. Command-line tools: https://developer.android.com/studio#command-line-tools-only"
		echo "  3. Set ANDROID_HOME environment variable"
		return 1
	fi

	local missing=""
	[ ! -d "$sdk_path/platforms" ] && missing+=" platforms"
	[ ! -d "$sdk_path/build-tools" ] && missing+=" build-tools"
	[ ! -d "$sdk_path/platform-tools" ] && missing+=" platform-tools"
	if [ -n "$missing" ]; then
		echo -e "${YELLOW}SDK incomplete (missing:$missing)${NC}"
		echo "Installing missing components..."
		local smgr
		smgr=$(sdkmanager_bin "$sdk_path")
		if [ -f "$smgr" ]; then
			yes | "$smgr" "platforms;android-34" "build-tools;34.0.0" "platform-tools"
		else
			echo "sdkmanager not found. Install via Android Studio SDK Manager."
		fi
	else
		echo -e "${GREEN}SDK OK${NC} (platforms, build-tools, platform-tools)"
	fi

	# Generate local.properties
	if [ -f "local.properties" ]; then
		local existing_key
		existing_key=$(grep "^gemini.api.key=" local.properties 2>/dev/null | cut -d'=' -f2-)
		if [ -n "$existing_key" ] && [ "$existing_key" != "YOUR_API_KEY_HERE" ]; then
			sed -i "s|^sdk.dir=.*|sdk.dir=$sdk_path|" local.properties
			echo -e "${GREEN}Updated local.properties${NC} (kept existing API key)"
		else
			cat > local.properties << EOF
sdk.dir=$sdk_path
gemini.api.key=YOUR_API_KEY_HERE
EOF
			echo -e "${GREEN}Generated local.properties${NC} (add your API key!)"
		fi
	else
		cat > local.properties << EOF
sdk.dir=$sdk_path
gemini.api.key=YOUR_API_KEY_HERE
EOF
		echo -e "${GREEN}Generated local.properties${NC} (add your API key!)"
	fi
}

do_build_debug() {
	echo -e "\n${CYAN}=== Build Debug APK ===${NC}"
	./gradlew assembleDebug
	echo -e "${GREEN}Build successful!${NC}"
	echo "APK: app/build/outputs/apk/debug/app-debug.apk"
}

do_install_emulator() {
	echo -e "\n${CYAN}=== Install on Emulator ===${NC}"
	local sdk_path
	sdk_path=$(resolve_sdk_path)
	local smgr
	smgr=$(sdkmanager_bin "$sdk_path")
	if [ ! -f "$smgr" ]; then
		echo -e "${RED}sdkmanager not found at: $smgr${NC}"
		echo "Install Android SDK first (option 1)"
		return 1
	fi

	echo "Installing emulator and system image (android-34, google_apis, x86_64)..."
	yes | "$smgr" "emulator" "system-images;android-34;google_apis;x86_64"

	local avdmgr
	avdmgr=$(avdmanager_bin "$sdk_path")
	echo "Creating AVD 'KnowledgeMapDevice'..."
	echo "no" | "$avdmgr" create avd -n "KnowledgeMapDevice" -k "system-images;android-34;google_apis;x86_64" || true
	echo -e "${GREEN}Emulator ready!${NC} AVD: KnowledgeMapDevice"
}

do_run_emulator() {
	echo -e "\n${CYAN}=== Run Emulator ===${NC}"
	local sdk_path
	sdk_path=$(resolve_sdk_path)
	local emu
	emu=$(emulator_bin "$sdk_path")

	if [ ! -f "$emu" ]; then
		echo -e "${RED}Emulator not found. Install it first (option 3)${NC}"
		return 1
	fi

	echo "Starting emulator..."
	"$emu" -avd KnowledgeMapDevice &
	echo "Waiting for emulator to boot..."
	local adb
	adb=$(adb_bin "$sdk_path")
	"$adb" wait-for-device
	sleep 10
	echo -e "${GREEN}Emulator running!${NC}"

	if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
		echo "Installing APK..."
		"$adb" install -r app/build/outputs/apk/debug/app-debug.apk
		echo -e "${GREEN}App installed!${NC} Launch with:"
		echo " $adb shell am start -n com.knowledgemap.app/com.knowledgemap.app.ui.MainActivity"
	else
		echo -e "${YELLOW}APK not found. Build first (option 2) then install.${NC}"
	fi
}

do_build_and_install() {
	echo -e "\n${CYAN}=== Build + Install on Device/Emulator ===${NC}"
	do_build_debug

	local sdk_path
	sdk_path=$(resolve_sdk_path)
	local adb
	adb=$(adb_bin "$sdk_path")

	local devices
	devices=$("$adb" devices | grep -v "List" | grep "device" | wc -l)
	if [ "$devices" -eq 0 ]; then
		echo -e "${YELLOW}No device/emulator running.${NC}"
		echo "Options:"
		echo " 1. Start emulator first (option 4)"
		echo " 2. Connect physical device via USB (with USB debugging enabled)"
		echo " 3. Install APK later manually"
		read -p "Start emulator now? (y/N) " -r
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			do_run_emulator
		else
			echo "APK ready at: app/build/outputs/apk/debug/app-debug.apk"
			return 0
		fi
	fi

	echo "Installing APK on device..."
	"$adb" install -r app/build/outputs/apk/debug/app-debug.apk
	echo -e "${GREEN}App installed!${NC} Launching..."
	"$adb" shell am start -n "com.knowledgemap.app/com.knowledgemap.app.ui.MainActivity"
}

do_backend_setup() {
	echo -e "\n${CYAN}=== Python Backend Setup ===${NC}"

	local python_cmd=""
	if command -v python3 &>/dev/null; then
		python_cmd="python3"
	elif command -v python &>/dev/null; then
		python_cmd="python"
	else
		echo -e "${RED}Python not found. Install Python 3.9+: https://python.org${NC}"
		return 1
	fi

	echo "Using: $($python_cmd --version)"

	if [ ! -d "backend/.venv" ]; then
		echo "Creating virtual environment..."
		$python_cmd -m venv backend/.venv
	else
		echo "Virtual environment already exists, reusing..."
	fi

	source backend/.venv/bin/activate

	echo "Installing Python dependencies..."
	pip install -r backend/requirements.txt -q
	echo -e "${GREEN}Backend setup complete.${NC}"
}

do_backend_run() {
	echo -e "\n${CYAN}=== Run Python Backend Server ===${NC}"

	if [ -f "backend/.venv/bin/activate" ]; then
		source backend/.venv/bin/activate
	else
		echo -e "${YELLOW}Virtual environment not found. Running setup first...${NC}"
		do_backend_setup
	fi

	if [ ! -f "backend/.env" ]; then
		echo -e "${RED}backend/.env not found!${NC}"
		return 1
	fi

	local key
	key=$(grep "^GEMINI_API_KEY=" backend/.env | cut -d'=' -f2-)
	if [ -z "$key" ] || [ "$key" = "YOUR_API_KEY_HERE" ]; then
		echo -e "${YELLOW}WARNING: Gemini API key not configured in backend/.env${NC}"
		echo "The server will start but AI features won't work."
		read -p "Continue? (y/N) " -r
		[[ ! $REPLY =~ ^[Yy]$ ]] && return 0
	fi

	echo -e "${GREEN}Starting backend server on http://localhost:8000${NC}"
	echo "Press Ctrl+C to stop"
	echo ""
	cd backend && uvicorn cognee_service.main:app --host 0.0.0.0 --port 8000 --reload
}

do_view_logcat() {
	echo -e "\n${CYAN}=== View Logcat (Live) ===${NC}"
	local sdk_path
	sdk_path=$(resolve_sdk_path)
	local adb
	adb=$(adb_bin "$sdk_path")

	if [ ! -f "$adb" ]; then
		echo -e "${RED}adb not found. Install platform-tools first (option 1)${NC}"
		return 1
	fi

	local devices
	devices=$("$adb" devices 2>/dev/null | grep -v "List" | grep "device" | wc -l)
	if [ "$devices" -eq 0 ]; then
		echo -e "${RED}No device/emulator connected.${NC}"
		echo "Start emulator (option 4) or connect device via USB first."
		return 1
	fi

	echo "Showing live logcat for KnowledgeMap app..."
	echo "Filter: package=com.knowledgemap.app"
	echo "Press Ctrl+C to stop"
	echo ""
	"$adb" logcat --pid=$("$adb" shell pidof -s com.knowledgemap.app 2>/dev/null || echo 0) \
		-v time *:V 2>/dev/null || \
		"$adb" logcat -v time | grep -i "knowledgemap\|AndroidRuntime\|FATAL\|CRASH"
}

do_crash_log() {
	echo -e "\n${CYAN}=== Crash Log ===${NC}"
	local sdk_path
	sdk_path=$(resolve_sdk_path)
	local adb
	adb=$(adb_bin "$sdk_path")

	if [ ! -f "$adb" ]; then
		echo -e "${RED}adb not found. Install platform-tools first (option 1)${NC}"
		return 1
	fi

	local devices
	devices=$("$adb" devices 2>/dev/null | grep -v "List" | grep "device" | wc -l)
	if [ "$devices" -eq 0 ]; then
		echo -e "${RED}No device/emulator connected.${NC}"
		echo "Start emulator (option 4) or connect device via USB first."
		return 1
	fi

	local log_dir="logs"
	mkdir -p "$log_dir"
	local timestamp
	timestamp=$(date +%Y%m%d_%H%M%S)
	local log_file="$log_dir/crash_${timestamp}.log"

	echo "Dumping crash logs..."
	echo ""

	echo "=== FATAL EXCEPTIONS ===" > "$log_file"
	"$adb" logcat -d -s "AndroidRuntime:E" -v threadtime >> "$log_file" 2>/dev/null

	echo "" >> "$log_file"
	echo "=== APP LOGS (Errors & Warnings) ===" >> "$log_file"
	local pid
	pid=$("$adb" shell pidof -s com.knowledgemap.app 2>/dev/null || echo "0")
	if [ "$pid" != "0" ] && [ -n "$pid" ]; then
		"$adb" logcat -d --pid="$pid" -v threadtime *:W >> "$log_file" 2>/dev/null
	else
		"$adb" logcat -d -v threadtime | grep -i "knowledgemap" >> "$log_file" 2>/dev/null
	fi

	echo "" >> "$log_file"
	echo "=== SYSTEM CRASH ===" >> "$log_file"
	"$adb" logcat -d -b crash -v threadtime >> "$log_file" 2>/dev/null

	echo "" >> "$log_file"
	echo "=== DEVICE INFO ===" >> "$log_file"
	echo "Device: $("$adb" shell getprop ro.product.model 2>/dev/null)" >> "$log_file"
	echo "Android: $("$adb" shell getprop ro.build.version.release 2>/dev/null)" >> "$log_file"
	echo "SDK: $("$adb" shell getprop ro.build.version.sdk 2>/dev/null)" >> "$log_file"
	echo "App PID: $pid" >> "$log_file"

	local crash_count
	crash_count=$(grep -c "FATAL EXCEPTION\|AndroidRuntime\|Process.*com.knowledgemap.app.*died" "$log_file" 2>/dev/null || echo "0")

	if [ "$crash_count" -gt 0 ]; then
		echo -e "${RED}Found $crash_count crash(es)!${NC}"
		echo ""
		echo "--- Last crash ---"
		grep -A 20 "FATAL EXCEPTION" "$log_file" | tail -25
	else
		echo -e "${GREEN}No crash found in current logcat buffer.${NC}"
		echo "Tip: Reproduce the crash then re-run this option."
	fi

	echo ""
	echo -e "Full log saved: ${YELLOW}$log_file${NC}"
	echo "Share this file when reporting bugs."
}

do_run_all() {
	echo -e "\n${CYAN}=== Full Setup ===${NC}"
	do_sdk_setup || true
	do_backend_setup || true
	do_build_debug
	echo ""
	echo -e "${GREEN}=== Full Setup Complete ===${NC}"
	echo ""
	echo "Next steps:"
	echo "  1. Edit local.properties - add Gemini API key"
	echo "  2. Edit backend/.env - add Gemini API key"
	echo "  3. Start backend: re-run setup-unix.sh, option 7"
	echo "  4. Install on phone: re-run setup-unix.sh, option 5"
}

# --- Menu ---
show_menu() {
	echo ""
	echo -e "${CYAN}===========================================${NC}"
	echo -e "${CYAN} KnowledgeMap Learning App - Setup Menu ${NC}"
	echo -e "${CYAN}===========================================${NC}"
	echo -e " OS: ${GREEN}$OS${NC}"
	echo ""
	echo -e " ${YELLOW}Android SDK:${NC}"
	echo "  1. Setup Android SDK (local.properties)"
	echo "  2. Build Debug APK"
	echo "  3. Install Emulator + System Image"
	echo "  4. Start Emulator"
	echo "  5. Build + Install on Device/Emulator"
	echo ""
	echo -e " ${YELLOW}Python Backend:${NC}"
	echo "  6. Setup Backend (venv + pip install)"
	echo "  7. Run Backend Server"
	echo ""
	echo -e " ${YELLOW}Debug:${NC}"
	echo "  8. View Logcat (live)"
	echo "  9. Crash Log (dump + save to file)"
	echo ""
	echo -e " ${YELLOW}Other:${NC}"
	echo "  10. Full Setup (1 + 2 + 6)"
	echo "  0. Exit"
	echo ""
}

# --- Main ---
main() {
	if [ ! -f "gradlew" ]; then
		echo "ERROR: Run this script from the project root directory"
		exit 1
	fi

	if [ -n "$1" ]; then
		case "$1" in
		sdk) do_sdk_setup ;;
		build) do_build_debug ;;
		emu) do_install_emulator ;;
		run-emu) do_run_emulator ;;
		install) do_build_and_install ;;
		backend) do_backend_setup ;;
		serve) do_backend_run ;;
		logcat) do_view_logcat ;;
		crash) do_crash_log ;;
		all) do_run_all ;;
		*) echo "Usage: ./setup-unix.sh [sdk|build|emu|run-emu|install|backend|serve|logcat|crash|all]" ;;
		esac
		return
	fi

	while true; do
		show_menu
		read -p " Choose option: " choice
		case "$choice" in
		1) do_sdk_setup ;;
		2) do_build_debug ;;
		3) do_install_emulator ;;
		4) do_run_emulator ;;
		5) do_build_and_install ;;
		6) do_backend_setup ;;
		7) do_backend_run ;;
		8) do_view_logcat ;;
		9) do_crash_log ;;
		10) do_run_all ;;
		0) echo "Bye!"; exit 0 ;;
		*) echo -e "${RED}Invalid option${NC}" ;;
		esac
		echo ""
		read -p "Press Enter to continue..."
	done
}

main "$@"
