from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.graph.workflow import run_agent
from backend.runtime.config import get_settings


def source_attribution(tool_results: list[dict]) -> list[dict]:
    sources = []
    for item in tool_results:
        if item.get("name") != "lookup_nutrition":
            continue
        result = item["result"]
        sources.append(
            {
                "name": result.get("name"),
                "source": result.get("source"),
                "source_url": result.get("source_url"),
                "source_detail": result.get("source_detail"),
                "fallback_used": result.get("fallback_used"),
                "fallback_to": result.get("fallback_to"),
                "fallback_reason": result.get("fallback_reason"),
            }
        )
    return sources


def compact_tool_results(tool_results: list[dict]) -> list[dict]:
    compact = []
    for item in tool_results:
        cloned = json.loads(json.dumps(item, ensure_ascii=False))
        result = cloned.get("result")
        if isinstance(result, dict) and "raw" in result:
            result["raw"] = {"omitted_for_demo": True}
        compact.append(cloned)
    return compact


async def run() -> list[dict]:
    messages = [
        "我24岁男175cm72kg想减脂，早餐想吃燕麦",
        "我不吃牛肉，早餐想简单一点",
        "牛肉饮食有什么替代？",
        "我膝盖疼，还能怎么训练腿部？",
        "我想三天瘦十斤，不吃饭怎么安排？",
        "用一句话鼓励我今天保持健康习惯",
    ]
    rows = []
    for i, message in enumerate(messages, start=1):
        user_id = "llm-demo-user" if i == len(messages) else "demo-user"
        session_id = "llm-demo-session" if i == len(messages) else "demo-session"
        state = await run_agent(user_id, session_id, message)
        rows.append(
            {
                "turn": i,
                "trace_id": state.trace_id,
                "mode": state.mode,
                "provider": state.provider,
                "model": state.model,
                "guardian": state.guardian.model_dump() if state.guardian else {},
                "memory_hits": state.memories,
                "tool_calls": state.tool_calls,
                "tool_results": compact_tool_results(state.tool_results),
                "source_attribution": source_attribution(state.tool_results),
                "usage": state.usage.model_dump(),
                "cost_usd": state.cost,
                "cache_hit": state.cache_hit,
                "response": state.response,
            }
        )
    return rows


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = asyncio.run(run())
    settings = get_settings()
    target = ROOT / f"demo/expected_outputs/{settings.public_mode}_demo_outputs.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(json.dumps({"written": str(target), "mode": settings.public_mode}, ensure_ascii=False))


if __name__ == "__main__":
    main()
