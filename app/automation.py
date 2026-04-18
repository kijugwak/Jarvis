from __future__ import annotations

from datetime import datetime


def build_morning_brief() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"[아침 브리핑] {now}\n"
        "- 오늘 최우선 1가지 목표를 정하세요.\n"
        "- 오전/오후 각 1개 핵심 작업만 먼저 완료하세요.\n"
        "- 끝나면 3줄 회고를 기록하세요."
    )
