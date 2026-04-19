from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

import requests

GOOGLE_NEWS_KR_RSS = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"


@dataclass
class NewsItem:
    title: str
    link: str
    published_at: str


def _fmt_pub_date(raw: str | None) -> str:
    if not raw:
        return "-"
    try:
        dt = parsedate_to_datetime(raw).astimezone()
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return raw.strip()


def fetch_top_news(limit: int = 5) -> list[NewsItem]:
    resp = requests.get(GOOGLE_NEWS_KR_RSS, timeout=10)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    channel = root.find("channel")
    if channel is None:
        return []

    items: list[NewsItem] = []
    for item in channel.findall("item")[: max(1, limit)]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_raw = item.findtext("pubDate")
        items.append(NewsItem(title=title, link=link, published_at=_fmt_pub_date(pub_raw)))
    return items


def build_news_digest(limit: int = 5) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = fetch_top_news(limit=limit)
    if not rows:
        return f"[오늘 뉴스] {now}\n가져온 뉴스가 없어요."
    lines = [f"[오늘 뉴스] {now}"]
    for i, n in enumerate(rows, start=1):
        lines.append(f"{i}. {n.title} ({n.published_at})")
        lines.append(f"   {n.link}")
    return "\n".join(lines)
