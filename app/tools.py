from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote_plus

from .news import build_news_digest


@dataclass
class ToolResult:
    handled: bool
    message: str


SITE_MAP = {
    "naver": "https://www.naver.com",
    "네이버": "https://www.naver.com",
    "google": "https://www.google.com",
    "구글": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "유튜브": "https://www.youtube.com",
    "github": "https://github.com",
    "깃허브": "https://github.com",
    "gmail": "https://mail.google.com",
    "메일": "https://mail.google.com",
    "calendar": "https://calendar.google.com",
    "캘린더": "https://calendar.google.com",
    "notion": "https://www.notion.so",
    "노션": "https://www.notion.so",
}


APP_MAP = {
    "터미널": "Terminal",
    "terminal": "Terminal",
    "크롬": "Google Chrome",
    "chrome": "Google Chrome",
    "카카오톡": "KakaoTalk",
    "kakaotalk": "KakaoTalk",
    "notion app": "Notion",
}

APP_ALIASES = {
    "KakaoTalk": ["KakaoTalk", "카카오톡"],
    "Google Chrome": ["Google Chrome", "Chrome"],
}

APP_BUNDLE_IDS = {
    "KakaoTalk": [
        "com.kakao.KakaoTalkMac",
        "com.kakao.talk",
    ],
    "Google Chrome": [
        "com.google.Chrome",
    ],
}


def _activate_app(app_name: str) -> None:
    script = (
        'tell application "System Events"\n'
        f'  if exists process "{app_name}" then\n'
        f'    tell application process "{app_name}" to set frontmost to true\n'
        "  end if\n"
        "end tell"
    )
    subprocess.run(["osascript", "-e", script], check=False)


def _open_bundle(bundle_id: str) -> bool:
    p = subprocess.run(["open", "-b", bundle_id], check=False, capture_output=True, text=True)
    return p.returncode == 0


def _norm(text: str) -> str:
    return text.strip().lower()


def _open_chrome(url: str) -> ToolResult:
    try:
        subprocess.run(["open", "-a", "Google Chrome", url], check=True)
        return ToolResult(True, f"Chrome에서 {url} 를 열었어요.")
    except Exception as exc:
        return ToolResult(True, f"브라우저 실행 중 오류가 발생했어요: {exc}")


def _open_app(app_name: str) -> ToolResult:
    # 1) Try bundle ids first (more stable than display names).
    for bundle_id in APP_BUNDLE_IDS.get(app_name, []):
        if _open_bundle(bundle_id):
            try:
                _activate_app(app_name if app_name != "Google Chrome" else "Google Chrome")
            except Exception:
                pass
            return ToolResult(True, f"{app_name} 실행을 시도했어요.")

    # 2) Fallback to app display names.
    candidates = APP_ALIASES.get(app_name, [app_name])
    last_exc: Exception | None = None
    for candidate in candidates:
        try:
            subprocess.run(["open", "-a", candidate], check=True)
            try:
                _activate_app(candidate)
            except Exception:
                pass
            return ToolResult(True, f"{candidate} 실행을 시도했어요.")
        except Exception as exc:
            last_exc = exc
            continue

    # KakaoTalk deep-link fallback
    if app_name == "KakaoTalk":
        try:
            subprocess.run(["open", "kakaotalk://"], check=True)
            return ToolResult(True, "카카오톡 실행을 시도했어요.")
        except Exception as exc:
            last_exc = exc

    return ToolResult(True, f"{app_name} 실행 중 오류가 발생했어요: {last_exc}")


def _quick_status() -> str:
    loaded = "not loaded"
    running = "not running"
    try:
        p = subprocess.run(
            ["launchctl", "list"],
            check=False,
            capture_output=True,
            text=True,
        )
        if "com.gwaggiju.jarvis" in (p.stdout or ""):
            loaded = "loaded"
    except Exception:
        pass
    try:
        p2 = subprocess.run(
            ["pgrep", "-af", "app.wake_daemon"],
            check=False,
            capture_output=True,
            text=True,
        )
        if (p2.stdout or "").strip():
            running = "running"
    except Exception:
        pass
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"[Jarvis 상태] {now}\n- LaunchAgent: {loaded}\n- Voice daemon: {running}"


def try_local_tool(user_text: str) -> ToolResult:
    text = _norm(user_text)

    if any(k in text for k in ["몇시", "시간", "time"]):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return ToolResult(True, f"현재 시간은 {now} 입니다.")

    if text in {"안녕", "안녕 자비스", "hi", "hello"}:
        return ToolResult(True, "안녕하세요! 무엇을 도와드릴까요?")

    if any(k in text for k in ["상태", "status", "잘있어", "작동", "실행중"]):
        return ToolResult(True, _quick_status())

    wants_open = any(k in text for k in ["열어", "켜", "open", "실행"])
    wants_chrome = any(k in text for k in ["chrome", "크롬", "브라우저"])

    if wants_open and wants_chrome:
        for key, url in SITE_MAP.items():
            if key in text:
                return _open_chrome(url)

    url_match = re.search(r"(https?://[^\s]+)", user_text)
    if wants_open and wants_chrome and url_match:
        return _open_chrome(url_match.group(1))

    if any(k in text for k in ["검색", "search"]):
        if any(k in text for k in ["youtube", "유튜브"]):
            q = re.sub(
                r"(유튜브(에서)?|youtube|크롬|chrome|브라우저|에서|으로|로|에|"
                r"들어가서|들어가|가서|켜서|열어서|실행해서|검색(해줘|해 줘)?|search( for)?)",
                "",
                user_text,
                flags=re.IGNORECASE,
            ).strip()
            q = re.sub(r"\s+", " ", q).strip()
            if q:
                return _open_chrome(f"https://www.youtube.com/results?search_query={quote_plus(q)}")
            return ToolResult(True, "유튜브 검색어를 같이 말해 주세요. 예: 유튜브에서 AI 뉴스 검색해줘")

        q = user_text
        q = re.sub(r"(검색(해줘|해 줘)?|search( for)?)", "", q, flags=re.IGNORECASE).strip()
        if q:
            return _open_chrome(f"https://www.google.com/search?q={quote_plus(q)}")
        return ToolResult(True, "검색어를 같이 말해 주세요. 예: AI 에이전트 검색해줘")

    asks_news = any(k in text for k in ["오늘뉴스", "오늘 뉴스", "뉴스", "news"])
    if asks_news:
        try:
            return ToolResult(True, build_news_digest(limit=5))
        except Exception as exc:
            return ToolResult(True, f"뉴스를 가져오는 중 오류가 발생했어요: {exc}")

    if wants_open:
        for key, app in APP_MAP.items():
            if key in text:
                return _open_app(app)

        for key, url in SITE_MAP.items():
            if key in text:
                return _open_chrome(url)

    return ToolResult(False, "")
