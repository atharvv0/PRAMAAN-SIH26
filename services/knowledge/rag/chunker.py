"""
Chunker — splits document text into retrievable pieces before embedding.
Real, simple, no dependencies: splits on blank lines (paragraphs) and falls back
to fixed-size character windows for very long paragraphs, so no chunk is too big
for a useful embedding.
"""
from __future__ import annotations

MAX_CHUNK_CHARS = 800


def chunk_text(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    for para in paragraphs:
        if len(para) <= MAX_CHUNK_CHARS:
            chunks.append(para)
        else:
            for i in range(0, len(para), MAX_CHUNK_CHARS):
                chunks.append(para[i : i + MAX_CHUNK_CHARS])
    return chunks
