from __future__ import annotations

from backend.graph.state import AgentState
from backend.guardian.classifier import classify_guardian


def guardian_node(state: AgentState) -> AgentState:
    state.guardian = classify_guardian(state.message)
    state.audit["guardian"] = state.guardian.model_dump()
    return state
