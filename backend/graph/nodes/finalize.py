from __future__ import annotations

import json

from backend.graph.state import AgentState, UsageInfo
from backend.runtime.config import get_settings
from backend.runtime.llm import get_chat_client

SYSTEM_PROMPT = """你是 DailyFit Agent, 一个专业的健身和营养助手。

回复规则:
1. 只能使用工具结果里的营养数字和训练动作, 不要编造 kcal/protein/carb/fat。
2. 回复要直接解决用户问题, 给出具体可执行建议, 不要只复述工具结果。
3. 涉及伤病、极端减重或健康风险时, 先承接 Guardian 提醒, 不做医疗诊断。
4. 合理使用长期偏好, 但不要机械罗列所有 memory。
5. 营养数字必须说明来源, 如果是 computed, 说明它从哪个真实来源换算。
6. 如果 source 是 usda_sr_legacy_cache, 说明它是 USDA SR Legacy 缓存参考, 不要说成 live API 命中。
7. 控制在 100-250 字, 简体中文为主。

直接输出回复正文, 不要加“好的”“以下是”等开场白。"""


def _source_lines(state: AgentState) -> list[str]:
    lines = []
    for item in state.tool_results:
        if item.get("name") != "lookup_nutrition":
            continue
        result = item["result"]
        source = result["source"]
        computed_from = (result.get("raw") or {}).get("computed_from_source")
        if source == "computed" and computed_from:
            source = f"computed_from_{computed_from}"
        lines.append(
            f"{result['name']}: {result['kcal']} kcal, protein {result['protein_g']}g, "
            f"carb {result['carb_g']}g, fat {result['fat_g']}g per {result.get('serving_size_g') or 100}g "
            f"(source={source}, url={result.get('source_url') or 'n/a'}, "
            f"fallback={result.get('fallback_used', False)}, reason={result.get('fallback_reason') or 'n/a'})"
        )
    return lines


def _workout_lines(state: AgentState) -> list[str]:
    lines = []
    for item in state.tool_results:
        if item.get("name") != "plan_workout":
            continue
        plan = item["result"]
        exercise_names = [ex["name"] for ex in plan.get("exercises", [])]
        lines.append(f"Workout plan for {plan['goal']}: " + ", ".join(exercise_names[:5]))
        if plan.get("excluded"):
            lines.append(f"Excluded risky movements: {len(plan['excluded'])} by contraindication rules.")
    return lines


def _fallback_response(state: AgentState) -> str:
    state.audit["llm_used"] = False
    guardian = state.guardian
    memory_text = ""
    if state.memories:
        unique = []
        for hit in state.memories:
            if hit["summary"] not in unique:
                unique.append(hit["summary"])
        memory_text = "我参考了这些长期偏好：" + "；".join(unique)
    warning = ""
    if guardian and guardian.verdict in {"warn", "require_confirmation"}:
        warning = f"Guardian: {guardian.verdict} - {guardian.reason} "
    parts = [part for part in [warning, memory_text, *_source_lines(state), *_workout_lines(state)] if part]
    return "\n".join(parts)


def _relevant_memories(state: AgentState) -> list[dict]:
    query = state.message.lower()
    plan_keywords = {
        "计划",
        "推荐",
        "安排",
        "早餐",
        "晚餐",
        "训练",
        "热量",
        "宏量",
        "目标",
        "plan",
        "schedule",
        "calorie",
        "macro",
    }
    relevant = []
    seen = set()
    for hit in state.memories:
        summary = hit.get("summary", "")
        metadata = hit.get("metadata") or {}
        if not summary or summary in seen:
            continue
        is_profile = bool(metadata.get("profile")) or summary.startswith("用户资料")
        if is_profile and not any(keyword in query for keyword in plan_keywords):
            continue
        seen.add(summary)
        relevant.append(hit)
        if len(relevant) >= 3:
            break
    return relevant


def _compact_tool_results(state: AgentState) -> list[dict]:
    compact = []
    for item in state.tool_results:
        cloned = json.loads(json.dumps(item, ensure_ascii=False))
        result = cloned.get("result")
        if isinstance(result, dict) and "raw" in result:
            result["raw"] = {"omitted": True}
        compact.append(cloned)
    return compact


def _apply_usage(state: AgentState, response) -> None:
    state.mode = response.mode
    state.provider = response.provider
    state.model = response.model
    state.usage = UsageInfo(
        provider=response.provider,
        model=response.model,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
        cache_hit=response.cache_hit,
    )
    state.cost = response.cost_usd
    state.cache_hit = response.cache_hit
    token_count = response.input_tokens + response.output_tokens
    state.audit["llm_used"] = bool(token_count > 0 and not response.error)
    state.audit["llm_tokens"] = {
        "input": response.input_tokens,
        "output": response.output_tokens,
    }
    state.audit["llm_cost_usd"] = round(response.cost_usd or 0.0, 6)
    if response.error:
        state.audit["llm_error"] = response.error
        state.audit["llm_raw"] = response.raw


async def _synthesize_live_answer(state: AgentState) -> bool:
    settings = get_settings()
    if settings.mode != "live" or not settings.dashscope_api_key_present:
        return False
    client = get_chat_client()
    context = {
        "user_message": state.message,
        "guardian": state.guardian.model_dump() if state.guardian else {},
        "relevant_memory_hits": _relevant_memories(state),
        "tool_results": _compact_tool_results(state),
        "required_source_lines": _source_lines(state),
        "required_workout_lines": _workout_lines(state),
    }
    response = await client.generate(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(context, ensure_ascii=False)
                + "\n\n请综合这些上下文, 直接回答用户当前问题。",
            },
        ],
        temperature=0.2,
        purpose="chat",
    )
    if response.error or not response.content.strip():
        _apply_usage(state, response)
        return False
    state.response = response.content.strip()
    _apply_usage(state, response)
    return True


async def finalize_node(state: AgentState) -> AgentState:
    guardian = state.guardian
    if guardian and guardian.verdict == "deny":
        state.response = f"我不能提供这个请求的具体执行步骤。{guardian.safe_alternative or guardian.reason}"
        state.audit["llm_used"] = False
        return state

    has_context = bool(state.tool_results or state.memories or (guardian and guardian.verdict != "allow"))
    if has_context and await _synthesize_live_answer(state):
        return state
    if has_context:
        state.response = _fallback_response(state)
        return state

    client = get_chat_client()
    response = await client.generate(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": state.message},
        ],
        temperature=0.0,
        purpose="chat",
    )
    state.response = response.content
    _apply_usage(state, response)
    return state
