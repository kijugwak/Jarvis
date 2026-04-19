#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT_DIR/scripts/run_jarvis.sh"
PLIST_PATH="$HOME/Library/LaunchAgents/com.gwaggiju.jarvis.plist"
LOG_OUT="$HOME/Library/Logs/jarvis.out.log"
LOG_ERR="$HOME/Library/Logs/jarvis.err.log"
ACTION="${1:-help}"
DEBUG_LOG="$HOME/Library/Logs/jarvis.shortcut.log"

notify() {
  local title="$1"
  local body="$2"
  /usr/bin/osascript -e "display notification \"${body}\" with title \"${title}\"" >/dev/null 2>&1 || true
}

log_debug() {
  local msg="$1"
  {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg"
  } >> "$DEBUG_LOG"
}

prompt_retry_input() {
  local prompt="${1:-다시 입력해 주세요.}"
  /usr/bin/osascript <<EOF
set userInput to text returned of (display dialog "$prompt" default answer "" buttons {"취소", "전송"} default button "전송")
return userInput
EOF
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

prompt_followup_input() {
  local prompt="${1:-추가로 보낼 답장을 입력해 주세요.}"
  /usr/bin/osascript <<EOF
set userInput to text returned of (display dialog "$prompt" default answer "" buttons {"취소", "보내기"} default button "보내기")
return userInput
EOF
}

ask() {
  shift || true
  local query="${*:-}"
  # Fallback for shortcut invocations that pass input via stdin.
  if [[ -z "$query" ]]; then
    local stdin_text
    stdin_text="$(cat || true)"
    query="${stdin_text:-}"
  fi
  query="$(echo "$query" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

  log_debug "ask invoked. raw_query='${query}' action='$ACTION'"
  if [[ -z "$query" ]]; then
    log_debug "ask failed: empty query"
    echo "Usage: $0 ask \"질문 내용\""
    exit 1
  fi
  local output
  output="$("$ROOT_DIR/.venv/bin/python" -m app.siri_one_shot "$query" 2>&1)" || {
    log_debug "ask failed during python execution"
    echo "$output"
    exit 1
  }
  echo "$output"

  # If Jarvis asks for missing keywords (e.g., search query), prompt user to re-enter immediately.
  if echo "$output" | grep -Eq "검색어를 같이 말해 주세요|같이 말해 주세요"; then
    log_debug "ask requires retry input"
    local retry
    retry="$(prompt_retry_input "검색어를 못 알아들었어요. 다시 입력해 주세요.")" || true
    retry="$(echo "${retry:-}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [[ -n "$retry" ]]; then
      log_debug "ask retry with query='${retry}'"
      "$ROOT_DIR/.venv/bin/python" -m app.siri_one_shot "$retry" || true
    else
      log_debug "ask retry canceled or empty"
    fi
  fi

  # If Jarvis asks a confirmation/follow-up question, allow one more immediate user reply.
  if echo "$output" | grep -Eq "진행하시겠습니까|하시겠습니까|원하시나요|할까요\\?|괜찮을까요\\?"; then
    log_debug "ask follow-up prompt opened"
    local follow
    follow="$(prompt_followup_input "Jarvis가 확인 질문을 보냈어요. 답장을 입력해 주세요.")" || true
    follow="$(echo "${follow:-}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [[ -n "$follow" ]]; then
      log_debug "ask follow-up sent='${follow}'"
      "$ROOT_DIR/.venv/bin/python" -m app.siri_one_shot "$follow" || true
    else
      log_debug "ask follow-up canceled or empty"
    fi
  fi

  log_debug "ask completed"
}

ask_visible() {
  shift || true
  local query="${*:-}"
  if [[ -z "$query" ]]; then
    echo "Usage: $0 ask-visible \"질문 내용\""
    exit 1
  fi

  local escaped="${query//\\/\\\\}"
  escaped="${escaped//\"/\\\"}"
  local cmd="cd $ROOT_DIR; echo '=== JARVIS TASK START ==='; echo 'QUERY: $escaped'; echo; ./scripts/siri_jarvis.sh ask \"$escaped\"; echo; echo '=== JARVIS TASK END ==='"
  local script
  script=$(cat <<EOF
tell application "Terminal"
  activate
  do script "$cmd"
end tell
EOF
)
  /usr/bin/osascript -e "$script" >/dev/null 2>&1 || true
  echo "Opened Terminal progress view."
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
  ask-visible)
    ask_visible "$@"
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
Usage: $0 {start|ask|ask-visible|stop|briefing|work-start|status}
  start      Siri-only mode (disable always-listening daemon)
  ask        Run one Siri command (text -> Jarvis -> voice reply)
  ask-visible Run one Siri command in Terminal (visible progress)
  stop       Stop Jarvis agent/process
  briefing   Run morning briefing and notify
  work-start Open work apps and start Jarvis
  status     Show current status
EOF
    exit 1
    ;;
esac
