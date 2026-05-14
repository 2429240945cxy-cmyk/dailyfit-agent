from __future__ import annotations

from langgraph.graph import END, StateGraph

from backend.graph.nodes.finalize import finalize_node
from backend.graph.nodes.guardian import guardian_node
from backend.graph.nodes.intent_router import intent_node
from backend.graph.nodes.memory import memory_node
from backend.graph.nodes.reflect import reflect_node
from backend.graph.nodes.tool_selection import tool_selection_node
from backend.graph.nodes.tools import tools_node
from backend.graph.state import AgentState
from backend.runtime.audit_logger import AuditLogger, default_audit_record, new_trace_id
from backend.runtime.config import get_settings


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("guardian", guardian_node)
    graph.add_node("intent", intent_node)
    graph.add_node("memory", memory_node)
    graph.add_node("tool_selection", tool_selection_node)
    graph.add_node("tools", tools_node)
    graph.add_node("reflect", reflect_node)
    graph.add_node("finalize", finalize_node)
    graph.set_entry_point("guardian")

    def after_guardian(state: AgentState) -> str:
        return "finalize" if state.guardian and state.guardian.verdict == "deny" else "intent"

    graph.add_conditional_edges("guardian", after_guardian, {"finalize": "finalize", "intent": "intent"})
    graph.add_edge("intent", "memory")
    graph.add_edge("memory", "tool_selection")
    graph.add_edge("tool_selection", "tools")
    graph.add_edge("tools", "reflect")
    graph.add_edge("reflect", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


async def run_agent(user_id: str, session_id: str, message: str) -> AgentState:
    settings = get_settings()
    trace_id = new_trace_id()
    audit = default_audit_record(
        trace_id=trace_id,
        user_id=user_id,
        session_id=session_id,
        mode=settings.public_mode,
        provider=settings.llm_provider,
        model=settings.llm_model,
        message=message,
    )
    state = AgentState(
        user_id=user_id,
        session_id=session_id,
        message=message,
        mode=settings.public_mode,
        provider=settings.llm_provider,
        model=settings.llm_model,
        trace_id=trace_id,
        audit=audit,
    )
    app = build_graph()
    result = await app.ainvoke(state)
    if isinstance(result, dict):
        state = AgentState(**result)
    else:
        state = result
    state.audit.update(
        {
            "trace_id": state.trace_id,
            "mode": state.mode,
            "provider": state.provider,
            "model": state.model,
            "guardian": state.guardian.model_dump() if state.guardian else {},
            "intent": state.intent,
            "memory_hits": state.memories,
            "tool_calls": state.tool_calls,
            "tool_results": state.tool_results,
            "llm_usage": state.usage.model_dump(),
            "final_response": state.response,
        }
    )
    AuditLogger().write(state.audit)
    return state
