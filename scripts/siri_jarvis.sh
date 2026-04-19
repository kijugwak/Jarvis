#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT_DIR/scripts/run_jarvis.sh"
PLIST_PATH="$HOME/Library/LaunchAgents/com.gwaggiju.jarvis.plist"
LOG_OUT="$HOME/Library/Logs/jarvis.out.log"
LOG_ERR="$HOME/Library/Logs/jarvis.err.log"
ACTION="${1:-help}"

notify() {
  local title="$1"
  local body="$2"
  /usr/bin/osascript -e "display notification \"${body}\" with title \"${title}\"" >/dev/null 2>&1 || true
}

start_voice_daemon() {
  stop_jarvis >/dev/null 2>&1 || true
  local greet="Good evening, sir. Jarvis is now online."
  notify "Jarvis" "$greet"
  say -v "${TTS_VOICE:-Daniel}" -r "${TTS_RATE:-165}" "$greet" >/dev/null 2>&1 \
    || say -r "${TTS_RATE:-165}" "$greet" >/dev/null 2>&1 \
    || say "$greet" >/dev/null 2>&1 \
    || true
  echo "Jarvis Siri-only mode enabled. Greeting spoken."
}

stop_jarvis() {
  launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
  pkill -f "python -m app.voice_main" >/dev/null 2>&1 || true
  pkill -f "python -m app.wake_daemon" >/dev/null 2>&1 || true
  notify "Jarvis" "실행 중인 Jarvis를 중지했어요."
  echo "Jarvis stopped."
}

briefing() {
  local brief
  brief="$("$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/morning_brief.py")"
  notify "Jarvis 브리핑" "$brief"
  echo "$brief"
}

work_start() {
  open -a "Google Chrome" "https://mail.google.com" >/dev/null 2>&1 || true
  open -a "Google Chrome" "https://calendar.google.com" >/dev/null 2>&1 || true
  open -a "Google Chrome" "https://www.notion.so" >/dev/null 2>&1 || true
  start_voice_daemon
  notify "Jarvis" "업무 시작 세팅을 완료했어요."
  echo "Work-start automation complete."
}

ask() {
  shift || true
  local query="${*:-}"
  if [[ -z "$query" ]]; then
    echo "Usage: $0 ask \"질문 내용\""
    exit 1
  fi
  "$ROOT_DIR/.venv/bin/python" -m app.siri_one_shot "$query"
}

status() {
  if launchctl list | grep -q "com.gwaggiju.jarvis"; then
    echo "LaunchAgent: loaded"
  else
    echo "LaunchAgent: not loaded"
  fi
  if pgrep -f "app.wake_daemon" >/dev/null 2>&1; then
    echo "Voice daemon: running"
  else
    echo "Voice daemon: not running"
  fi
  echo "Logs:"
  echo " - $LOG_OUT"
  echo " - $LOG_ERR"
}

case "$ACTION" in
  start)
    start_voice_daemon
    ;;
  ask)
    ask "$@"
    ;;
  stop)
    stop_jarvis
    ;;
  briefing)
    briefing
    ;;
  work-start)
    work_start
    ;;
  status)
    status
    ;;
  *)
    cat <<EOF
Usage: $0 {start|ask|stop|briefing|work-start|status}
  start      Siri-only mode (disable always-listening daemon)
  ask        Run one Siri command (text -> Jarvis -> voice reply)
  stop       Stop Jarvis agent/process
  briefing   Run morning briefing and notify
  work-start Open work apps and start Jarvis
  status     Show current status
EOF
    exit 1
    ;;
esac
