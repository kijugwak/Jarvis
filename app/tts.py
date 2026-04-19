from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from .config import config


def to_speech_text(text: str) -> str:
    # Keep spoken output concise by stripping raw URLs.
    no_urls = re.sub(r"https?://\S+", "", text)
    lines = []
    for raw in no_urls.splitlines():
        ln = raw.strip()
        if not ln:
            continue
        # News header: skip timestamp and keep short intro only.
        if ln.startswith("[오늘 뉴스]"):
            lines.append("오늘 뉴스입니다.")
            continue
        # Drop trailing timestamp fragments like "(2026-04-18 20:47)".
        ln = re.sub(r"\(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\)\s*$", "", ln).strip()
        lines.append(ln)
    cleaned = "\n".join(lines)
    return cleaned.strip()


def speak(text: str) -> None:
    # macOS 기본 TTS를 우선 사용한다.
    try:
        cmd = ["say", "-r", str(config.tts_rate)]
        if config.tts_voice:
            cmd.extend(["-v", config.tts_voice])
        cmd.append(text)
        subprocess.run(cmd, check=True)
        return
    except Exception:
        pass

    # 기본 TTS 실패 시 로그만 남긴다.
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        f.write(text)
        temp = Path(f.name)
    print(f"[TTS fallback] {temp}")
