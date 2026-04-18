#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-menubar}"
PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
OLLAMA_BIN="${OLLAMA_BIN:-/opt/homebrew/bin/ollama}"
BREW_BIN="${BREW_BIN:-/opt/homebrew/bin/brew}"

cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  echo "[Jarvis] .venv 가 없습니다. 먼저 가상환경을 만들어주세요."
  exit 1
fi

source ".venv/bin/activate"

if [[ ! -x "$OLLAMA_BIN" ]]; then
  echo "[Jarvis] ollama 바이너리를 찾을 수 없습니다: $OLLAMA_BIN"
  exit 1
fi

if ! curl -sS "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
  echo "[Jarvis] Ollama 서버가 꺼져 있어 시작합니다."
  if [[ -x "$BREW_BIN" ]]; then
    "$BREW_BIN" services start ollama >/dev/null 2>&1 || true
  fi
  sleep 2
fi

case "$MODE" in
  menubar)
    exec python -m app.menubar
    ;;
  voice)
    exec python -m app.voice_main
    ;;
  daemon)
    exec python -m app.wake_daemon
    ;;
  *)
    echo "사용법: $0 [menubar|voice|daemon]"
    exit 1
    ;;
esac
