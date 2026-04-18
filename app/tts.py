from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def speak(text: str) -> None:
    # macOS 기본 TTS를 우선 사용한다.
    try:
        subprocess.run(["say", text], check=True)
        return
    except Exception:
        pass

    # 기본 TTS 실패 시 로그만 남긴다.
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        f.write(text)
        temp = Path(f.name)
    print(f"[TTS fallback] {temp}")
