from __future__ import annotations

import json

from backend.graph.state import AgentState, UsageInfo
from backend.runtime.config import get_settings
from backend.runtime.llm import get_chat_client


def _source_lines(state: AgentState) -> list[str]:
    lines = []
    for item in state.tool_results:
        if item.get("name") != "lookup_nutrition":
            continue
        result = item["result"]
        lines.append(
            f"{result['name']}: {result['kcal']} kcal, protein {result['protein_g']}g, "
            f"carb {result['carb_g']}g, fat {result['fat_g']}g per {result.get('serving_size_g') or 100}g "
            f"(source={result['source']}, url={result.get('source_url') or 'n/a'}, "
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
        "memory_hits": state.memories,
        "tool_results": _compact_tool_results(state),
        "required_source_lines": _source_lines(state),
        "required_workout_lines": _workout_lines(state),
    }
    response = await client.generate(
        [
            {
                "role": "system",
                "content": (
                    "You are DailyFit Agent, a practical fitness and nutrition assistant. "
                    "Answer the user's actual question in concise Chinese unless the user used English. "
                    "Use the provided tool results exactly; do not invent nutrition numbers or exercise data. "
                    "If a nutrition result has fallback_used=true, explicitly mention the fallback reason. "
                    "If Guardian is warn or require_confirmation, include a clear caution. "
                    "If Guardian is deny, do not provide steps. "
                    "Always cite source attribution when nutrition numbers appear."
                ),
            },
            {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
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
                "content": "You are DailyFit Agent. Give concise fitness and nutrition help. Do not invent nutrition numbers.",
            },
            {"role": "user", "content": state.message},
        ],
        temperature=0.0,
        purpose="chat",
    )
    state.response = response.content
    _apply_usage(state, response)
    return state
