from __future__ import annotations

from backend.graph.state import AgentState
from backend.memory.retrieval import search_memories
from backend.memory.store import MemoryStore
from backend.tools.profile_tools import update_profile_from_message


def memory_node(state: AgentState) -> AgentState:
    store = MemoryStore()
    hits = search_memories(state.message, store.list_by_user(state.user_id), top_k=3)
    state.memories = [hit.model_dump() for hit in hits]
    state.audit["memory_hits"] = state.memories
    created = update_profile_from_message(state.user_id, state.message, store)
    if created:
        state.audit["memory_created"] = created
    return state
