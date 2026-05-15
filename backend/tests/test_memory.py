from backend.memory.distiller import distill_memories
from backend.memory.retrieval import search_memories
from backend.memory.store import MemoryStore


def test_distiller_extracts_preference() -> None:
    memories = distill_memories("我不吃牛肉，早餐想简单")
    summaries = {m["summary"] for m in memories}
    assert "用户不吃牛肉" in summaries
    assert "用户喜欢简单早餐" in summaries


def test_distiller_extracts_synonym_constraints() -> None:
    memories = distill_memories("我吃不了红肉，喝奶不舒服，只能在家徒手练")
    summaries = {m["summary"] for m in memories}
    assert "用户不吃牛肉" in summaries
    assert "用户乳糖不耐" in summaries
    assert "用户在家训练/徒手" in summaries


def test_chinese_single_doc_overlap_hits_beef() -> None:
    store = MemoryStore(":memory:")
    store.add({"user_id": "u1", "type": "preference", "summary": "不吃牛肉", "retrievable_text": "用户不吃牛肉"})
    hits = search_memories("牛肉饮食", store.list_by_user("u1"), top_k=3)
    assert hits
    assert hits[0].summary == "不吃牛肉"


def test_memory_store_deduplicates_summary() -> None:
    store = MemoryStore(":memory:")
    first = store.add(
        {"user_id": "u1", "type": "preference", "summary": "用户不吃牛肉", "retrievable_text": "用户不吃牛肉"}
    )
    second = store.add(
        {"user_id": "u1", "type": "preference", "summary": "用户不吃牛肉", "retrievable_text": "用户不吃牛肉"}
    )
    memories = store.list_by_user("u1")
    assert first.id == second.id
    assert len(memories) == 1


def test_retrieval_deduplicates_existing_duplicate_summaries() -> None:
    store = MemoryStore(":memory:")
    with store._connect() as conn:
        conn.executemany(
            """
            insert into memory
            (id, user_id, type, summary, retrievable_text, metadata, created_at, updated_at)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("m1", "u1", "preference", "用户不吃牛肉", "用户不吃牛肉", "{}", "2026-01-01", "2026-01-01"),
                ("m2", "u1", "preference", "用户不吃牛肉", "用户不吃牛肉", "{}", "2026-01-02", "2026-01-02"),
            ],
        )
    hits = search_memories("牛肉饮食", store.list_by_user("u1"), top_k=3)
    assert [hit.summary for hit in hits] == ["用户不吃牛肉"]


def test_retrieval_expands_synonyms() -> None:
    store = MemoryStore(":memory:")
    store.add(
        {"user_id": "u1", "type": "constraint", "summary": "用户不吃牛肉", "retrievable_text": "用户不吃牛肉"}
    )
    hits = search_memories("推荐高蛋白晚餐，要红肉替代品", store.list_by_user("u1"), top_k=3)
    assert hits
    assert hits[0].summary == "用户不吃牛肉"


def test_retrieval_avoids_common_char_false_positive() -> None:
    store = MemoryStore(":memory:")
    store.add(
        {"user_id": "u1", "type": "constraint", "summary": "用户不吃牛肉", "retrievable_text": "用户不吃牛肉"}
    )
    hits = search_memories("我今天想吃鱼", store.list_by_user("u1"), top_k=3)
    assert hits == []
