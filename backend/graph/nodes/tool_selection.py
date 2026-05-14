from __future__ import annotations

from backend.graph.state import AgentState


def tool_selection_node(state: AgentState) -> AgentState:
    calls = []
    if state.intent in {"nutrition", "meal_log", "profile_update", "general"}:
        if any(
            term in state.message.lower()
            for term in [
                "燕麦",
                "oat",
                "rice",
                "米饭",
                "鸡胸",
                "banana",
                "牛奶",
                "鸡蛋",
                "早餐",
                "吃",
            ]
        ):
            calls.append({"name": "lookup_nutrition", "args": {"query": state.message}})
    if state.intent in {"workout", "general"}:
        if any(term in state.message.lower() for term in ["训练", "workout", "exercise", "计划"]):
            constraints = []
            if any(term in state.message for term in ["膝盖", "knee"]):
                constraints.append("knee pain")
            if any(term in state.message for term in ["肩", "shoulder"]):
                constraints.append("shoulder injury")
            if any(term in state.message for term in ["腰", "back"]):
                constraints.append("lower back pain")
            calls.append({"name": "plan_workout", "args": {"goal": state.message, "constraints": constraints}})
    state.tool_calls = calls
    state.audit["tool_calls"] = calls
    return state
