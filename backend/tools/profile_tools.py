from __future__ import annotations

from backend.memory.distiller import distill_memories
from backend.memory.store import MemoryStore


def update_profile_from_message(user_id: str, message: str, store: MemoryStore | None = None) -> list[dict]:
    store = store or MemoryStore()
    created = []
    for item in distill_memories(message):
        memory = store.add({"user_id": user_id, **item})
        created.append(memory.model_dump())
    return created
