from __future__ import annotations

from backend.graph.state import AgentState, UsageInfo
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
            f"(source={result['source']}, url={result.get('source_url') or 'n/a'})"
        )
    return lines


def _workout_lines(state: AgentState) -> list[str]:
    lines = []
    for item in state.tool_results:
        if item.get("name") != "plan_workout":
            continue
        plan = item["result"]
        exercise_names = [ex["name"] for ex in plan.get("exercises", [])]
        lines.append(
            f"Workout plan for {plan['goal']}: " + ", ".join(exercise_names[:5])
        )
        if plan.get("excluded"):
            lines.append(f"Excluded risky movements: {len(plan['excluded'])} by contraindication rules.")
    return lines


async def finalize_node(state: AgentState) -> AgentState:
    guardian = state.guardian
    if guardian and guardian.verdict == "deny":
        state.response = f"我不能提供这个请求的具体执行步骤。{guardian.safe_alternative or guardian.reason}"
        return state

    memory_text = ""
    if state.memories:
        memory_text = "我参考了这些长期偏好：" + "；".join(hit["summary"] for hit in state.memories)

    source_lines = _source_lines(state)
    workout_lines = _workout_lines(state)
    warning = ""
    if guardian and guardian.verdict in {"warn", "require_confirmation"}:
        warning = f"Guardian: {guardian.verdict} - {guardian.reason} "

    if source_lines or workout_lines or warning or memory_text:
        parts = [part for part in [warning, memory_text, *source_lines, *workout_lines] if part]
        state.response = "\n".join(parts)
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
    return state
