#!/usr/bin/env bash
set -euo pipefail

cd /Users/gwaggiju/Jarvis

CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
DIM="\033[2m"
RESET="\033[0m"

BANNER_TEXT="${ACTIVATION_BANNER_TEXT:-JARVIS ONLINE}"

clear
printf "${CYAN}"
printf "╔════════════════════════════════════════════╗\n"
printf "║ %-42s ║\n" "$BANNER_TEXT"
printf "╚════════════════════════════════════════════╝\n"
printf "${RESET}\n"

printf "${GREEN}SYSTEM${RESET}  %s\n" "$(date '+%Y-%m-%d %H:%M:%S')"
printf "${YELLOW}INPUT${RESET}   %s\n" "${AUDIO_INPUT_DEVICE:-default}"
printf "${YELLOW}VOICE${RESET}   %s  @ rate %s\n" "${TTS_VOICE:-default}" "${TTS_RATE:-165}"
printf "${DIM}Live logs (Ctrl+C to close this terminal view)${RESET}\n\n"

tail -n 80 -f ~/Library/Logs/jarvis.out.log
