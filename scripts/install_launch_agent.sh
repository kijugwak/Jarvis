#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-menubar}"
INPUT_DEVICE="${2:-MacBook Pro 마이크}"
TTS_VOICE="${3:-Samantha}"
TTS_RATE="${4:-165}"
VOICE_AUTH_ENABLED="${5:-1}"
VOICE_AUTH_THRESHOLD="${6:-0.84}"
VOICE_PROFILE_PATH="${7:-$ROOT_DIR/data/voice/owner.npy}"
SHOW_TERMINAL_ON_WAKE="${8:-1}"
WAKE_TERMINAL_COOLDOWN_SEC="${9:-8}"
ACTIVATION_SOUND_ENABLED="${10:-1}"
ACTIVATION_SOUND_FILE="${11:-/System/Library/Sounds/Glass.aiff}"
ACTIVATION_BANNER_TEXT="${12:-JARVIS ONLINE}"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/com.gwaggiju.jarvis.plist"
LOG_DIR="$HOME/Library/Logs"

mkdir -p "$PLIST_DIR"
mkdir -p "$LOG_DIR"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.gwaggiju.jarvis</string>

  <key>ProgramArguments</key>
  <array>
    <string>$ROOT_DIR/scripts/run_jarvis.sh</string>
    <string>$MODE</string>
  </array>

  <key>WorkingDirectory</key>
  <string>$ROOT_DIR</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>AUDIO_INPUT_DEVICE</key>
    <string>$INPUT_DEVICE</string>
    <key>TTS_VOICE</key>
    <string>$TTS_VOICE</string>
    <key>TTS_RATE</key>
    <string>$TTS_RATE</string>
    <key>VOICE_AUTH_ENABLED</key>
    <string>$VOICE_AUTH_ENABLED</string>
    <key>VOICE_AUTH_THRESHOLD</key>
    <string>$VOICE_AUTH_THRESHOLD</string>
    <key>VOICE_PROFILE_PATH</key>
    <string>$VOICE_PROFILE_PATH</string>
    <key>SHOW_TERMINAL_ON_WAKE</key>
    <string>$SHOW_TERMINAL_ON_WAKE</string>
    <key>WAKE_TERMINAL_COOLDOWN_SEC</key>
    <string>$WAKE_TERMINAL_COOLDOWN_SEC</string>
    <key>ACTIVATION_SOUND_ENABLED</key>
    <string>$ACTIVATION_SOUND_ENABLED</string>
    <key>ACTIVATION_SOUND_FILE</key>
    <string>$ACTIVATION_SOUND_FILE</string>
    <key>ACTIVATION_BANNER_TEXT</key>
    <string>$ACTIVATION_BANNER_TEXT</string>
    <key>PYTHONUNBUFFERED</key>
    <string>1</string>
  </dict>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <true/>

  <key>StandardOutPath</key>
  <string>$LOG_DIR/jarvis.out.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/jarvis.err.log</string>
</dict>
</plist>
EOF

chmod +x "$ROOT_DIR/scripts/run_jarvis.sh"

launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl load "$PLIST_PATH"

echo "[Jarvis] LaunchAgent 설치 완료: $PLIST_PATH"
echo "[Jarvis] 실행 모드: $MODE"
echo "[Jarvis] 입력 장치: $INPUT_DEVICE"
echo "[Jarvis] TTS 보이스: $TTS_VOICE"
echo "[Jarvis] TTS 속도: $TTS_RATE"
echo "[Jarvis] Voice Auth: $VOICE_AUTH_ENABLED (threshold=$VOICE_AUTH_THRESHOLD)"
echo "[Jarvis] Voice Profile: $VOICE_PROFILE_PATH"
echo "[Jarvis] Show Terminal On Wake: $SHOW_TERMINAL_ON_WAKE (cooldown=${WAKE_TERMINAL_COOLDOWN_SEC}s)"
echo "[Jarvis] Activation Sound: $ACTIVATION_SOUND_ENABLED ($ACTIVATION_SOUND_FILE)"
echo "[Jarvis] Activation Banner: $ACTIVATION_BANNER_TEXT"
echo "[Jarvis] 로그: $LOG_DIR/jarvis.out.log / $LOG_DIR/jarvis.err.log"
