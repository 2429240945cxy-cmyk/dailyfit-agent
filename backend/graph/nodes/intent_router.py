from __future__ import annotations

from backend.graph.state import AgentState


def detect_intent(message: str) -> str:
    text = message.lower()
    if any(term in text for term in ["忽略之前", "ignore previous", "api key"]):
        return "unsafe_health"
    if any(term in text for term in ["卡路里", "营养", "蛋白", "吃", "早餐", "meal", "food", "kcal"]):
        return "nutrition"
    if any(term in text for term in ["训练", "workout", "exercise", "计划", "膝盖疼", "肩伤", "腰伤"]):
        return "workout"
    if any(term in text for term in ["记录", "log", "早餐吃了", "午餐吃了"]):
        return "meal_log"
    if any(term in text for term in ["不吃", "偏好", "目标", "cm", "kg", "岁"]):
        return "profile_update"
    if any(term in text for term in ["记得", "memory", "偏好是什么"]):
        return "memory_query"
    return "general"


def intent_node(state: AgentState) -> AgentState:
    state.intent = detect_intent(state.message)
    state.audit["intent"] = state.intent
    return state
