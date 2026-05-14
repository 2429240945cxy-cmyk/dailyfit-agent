from backend.memory.distiller import distill_memories
from backend.memory.retrieval import search_memories
from backend.memory.store import MemoryStore


def test_distiller_extracts_preference() -> None:
    memories = distill_memories("我不吃牛肉，早餐想简单")
    summaries = {m["summary"] for m in memories}
    assert "用户不吃牛肉" in summaries
    assert "用户喜欢简单早餐" in summaries


def test_chinese_single_doc_overlap_hits_beef() -> None:
    store = MemoryStore(":memory:")
    store.add({"user_id": "u1", "type": "preference", "summary": "不吃牛肉", "retrievable_text": "用户不吃牛肉"})
    hits = search_memories("牛肉饮食", store.list_by_user("u1"), top_k=3)
    assert hits
    assert hits[0].summary == "不吃牛肉"
