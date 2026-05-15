from __future__ import annotations

import math

from backend.memory.schemas import MemoryHit


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    size = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(size))
    na = math.sqrt(sum(a[i] * a[i] for i in range(size))) or 1.0
    nb = math.sqrt(sum(b[i] * b[i] for i in range(size))) or 1.0
    return dot / (na * nb)


def merge_hits(primary: list[MemoryHit], secondary: list[MemoryHit], top_k: int = 3) -> list[MemoryHit]:
    merged: dict[str, MemoryHit] = {}
    for hit in primary + secondary:
        key = hit.summary.strip().lower() or hit.retrievable_text.strip().lower() or hit.id
        if key not in merged or hit.score > merged[key].score:
            merged[key] = hit
    return sorted(merged.values(), key=lambda hit: hit.score, reverse=True)[:top_k]
