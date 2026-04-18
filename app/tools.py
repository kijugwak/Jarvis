from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolResult:
    handled: bool
    message: str


def _open_chrome(url: str) -> ToolResult:
    try:
        subprocess.run(["open", "-a", "Google Chrome", url], check=True)
        return ToolResult(True, f"Chrome에서 {url} 를 열었어요.")
    except Exception as exc:
        return ToolResult(True, f"브라우저 실행 중 오류가 발생했어요: {exc}")


def try_local_tool(user_text: str) -> ToolResult:
    text = user_text.strip().lower()

    if any(k in text for k in ["몇시", "시간", "time"]):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return ToolResult(True, f"현재 시간은 {now} 입니다.")

    if text in {"안녕", "안녕 자비스", "hi", "hello"}:
        return ToolResult(True, "안녕하세요! 무엇을 도와드릴까요?")

    wants_open = any(k in text for k in ["열어", "켜", "open", "실행"])
    wants_chrome = any(k in text for k in ["chrome", "크롬"])

    if wants_open and wants_chrome:
        if "naver" in text or "네이버" in text:
            return _open_chrome("https://www.naver.com")

    url_match = re.search(r"(https?://[^\s]+)", user_text)
    if wants_open and wants_chrome and url_match:
        return _open_chrome(url_match.group(1))

    return ToolResult(False, "")
