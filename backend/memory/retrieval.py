from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from backend.memory.schemas import MemoryHit, MemoryItem

CHINESE_STOP_CHARS = set("我你他她它的了和是要想给帮还按吗呢啊吧就都很有在不吃今天")

SYNONYM_GROUPS = [
    {"牛肉", "红肉", "beef", "red meat", "牛排"},
    {"膝盖", "膝", "knee", "腿部"},
    {"肩", "肩膀", "肩部", "shoulder", "推举"},
    {"腰", "背", "lower back", "back"},
    {"减脂", "减重", "减肥", "瘦", "cutting", "cut"},
    {"增肌", "增重", "壮", "bulk", "muscle", "gain muscle"},
    {"中餐", "中国菜", "chinese food", "chinese style"},
    {"预算", "预算低", "省钱", "便宜", "low budget", "cheap"},
    {"早餐", "快手", "simple breakfast", "quick breakfast"},
    {"乳糖", "乳制品", "牛奶", "milk-free", "lactose"},
    {"素食", "vegetarian", "vegan", "不吃肉"},
    {"马拉松", "marathon", "长跑", "carb loading"},
]


def expand_with_synonyms(tokens: list[str], text: str) -> list[str]:
    expanded = set(tokens)
    lowered = text.lower()
    for group in SYNONYM_GROUPS:
        if any(term in lowered or term in expanded for term in group):
            expanded.update(group)
    return list(expanded)


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    latin = re.findall(r"[a-z0-9]+", lowered)
    cjk = [char for char in re.findall(r"[\u4e00-\u9fff]", lowered) if char not in CHINESE_STOP_CHARS]
    words = []
    for phrase in [
        "牛肉",
        "红肉",
        "膝盖",
        "减脂",
        "增肌",
        "早餐",
        "中餐",
        "乳糖",
        "乳制品",
        "素食",
        "马拉松",
        "预算",
        "肩伤",
        "肩部",
        "长跑",
    ]:
        if phrase in lowered:
            words.append(phrase)
    return expand_with_synonyms(latin + cjk + words, lowered)


def lexical_overlap(query_tokens: set[str], doc_tokens: set[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    intersection = query_tokens & doc_tokens
    return len(intersection) / max(1, len(query_tokens))


def search_memories(query: str, memories: list[MemoryItem], top_k: int = 3) -> list[MemoryHit]:
    if not memories:
        return []
    query_tokens = tokenize(query)
    docs = [tokenize(memory.retrievable_text + " " + memory.summary) for memory in memories]
    bm25_scores = [0.0 for _ in memories]
    if len(memories) >= 2:
        bm25 = BM25Okapi(docs)
        bm25_scores = list(map(float, bm25.get_scores(query_tokens)))
    qset = set(query_tokens)
    ranked = []
    for memory, doc_tokens, bm25_score in zip(memories, docs, bm25_scores, strict=True):
        overlap = lexical_overlap(qset, set(doc_tokens))
        score = bm25_score + overlap * 2.0
        if bm25_score <= 0 and overlap > 0:
            score = max(score, overlap)
        if score > 0:
            ranked.append(
                MemoryHit(
                    id=memory.id,
                    summary=memory.summary,
                    retrievable_text=memory.retrievable_text,
                    score=round(score, 4),
                    source="bm25_lexical",
                    metadata=memory.metadata,
                )
            )
    ranked.sort(key=lambda hit: hit.score, reverse=True)
    deduped: list[MemoryHit] = []
    seen: set[str] = set()
    for hit in ranked:
        key = hit.summary.strip().lower() or hit.retrievable_text.strip().lower() or hit.id
        if key in seen:
            continue
        seen.add(key)
        deduped.append(hit)
        if len(deduped) >= top_k:
            break
    return deduped
