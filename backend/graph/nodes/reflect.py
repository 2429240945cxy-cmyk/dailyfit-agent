from __future__ import annotations

from backend.graph.state import AgentState


def reflect_node(state: AgentState) -> AgentState:
    checks = {
        "nutrition_source_cited": any(
            result.get("name") == "lookup_nutrition" for result in state.tool_results
        ),
        "guardian_visible": state.guardian is not None and state.guardian.verdict != "allow",
        "memory_hits_used": bool(state.memories),
        "live_usage_tokens": state.mode != "live_real"
        or (state.usage.input_tokens + state.usage.output_tokens > 0),
        "fallback_visible": bool(state.audit.get("nutrition_source_fallback")),
    }
    state.audit["reflect"] = checks
    return state
