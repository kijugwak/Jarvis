#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-menubar}"
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
echo "[Jarvis] 로그: $LOG_DIR/jarvis.out.log / $LOG_DIR/jarvis.err.log"
