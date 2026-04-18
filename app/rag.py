from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from .config import config


@dataclass
class Chunk:
    source: str
    text: str


def _tokenize(text: str) -> list[str]:
    # Korean/English/numbers only for simple lexical retrieval.
    return re.findall(r"[가-힣a-zA-Z0-9]+", text.lower())


def _split_text(text: str, chunk_size: int, overlap: int) -> Iterable[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    result: list[str] = []
    start = 0
    n = len(cleaned)
    while start < n:
        end = min(start + chunk_size, n)
        result.append(cleaned[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return result


def _load_knowledge_chunks() -> list[Chunk]:
    base = Path(config.knowledge_dir)
    if not base.exists():
        return []
    chunks: list[Chunk] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in config.knowledge_extensions:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for part in _split_text(text, config.rag_chunk_size, config.rag_chunk_overlap):
            chunks.append(Chunk(source=str(path), text=part))
    return chunks


def retrieve_context(query: str, top_k: int | None = None) -> list[Chunk]:
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return []

    k = top_k if top_k is not None else config.rag_top_k
    chunks = _load_knowledge_chunks()
    scored: list[tuple[int, Chunk]] = []
    for chunk in chunks:
        c_tokens = set(_tokenize(chunk.text))
        score = len(q_tokens & c_tokens)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]


def format_context(chunks: list[Chunk]) -> str:
    if not chunks:
        return ""
    lines = []
    for idx, chunk in enumerate(chunks, start=1):
        lines.append(f"[{idx}] source={chunk.source}\n{chunk.text}")
    return "\n\n".join(lines)
