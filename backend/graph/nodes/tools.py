from __future__ import annotations

from backend.graph.state import AgentState
from backend.tools.nutrition_tools import lookup_nutrition
from backend.tools.workout_tools import plan_workout


async def tools_node(state: AgentState) -> AgentState:
    results = []
    for call in state.tool_calls:
        if call["name"] == "lookup_nutrition":
            result = await lookup_nutrition(**call["args"])
            payload = result.model_dump()
            results.append({"name": "lookup_nutrition", "result": payload})
            if result.fallback_used:
                state.audit["nutrition_source_fallback"] = {
                    "fallback_used": True,
                    "fallback_from": result.fallback_from,
                    "fallback_to": result.fallback_to,
                    "fallback_reason": result.fallback_reason,
                }
        elif call["name"] == "plan_workout":
            args = dict(call["args"])
            if state.guardian and "injury_training" in state.guardian.risk_categories:
                constraints = list(args.get("constraints") or [])
                constraints.extend(["injury_training", state.guardian.reason])
                if state.guardian.safe_alternative:
                    constraints.append(state.guardian.safe_alternative)
                args["constraints"] = constraints
            result = plan_workout(**args)
            payload = result.model_dump()
            results.append({"name": "plan_workout", "result": payload})
            state.audit["workout_plan"] = payload
    state.tool_results = results
    state.audit["tool_results"] = results
    return state
