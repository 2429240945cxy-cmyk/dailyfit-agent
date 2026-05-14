from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.graph.workflow import run_agent


async def run() -> list[dict]:
    messages = [
        "我24岁男175cm72kg想减脂，早餐想吃燕麦",
        "我不吃牛肉，早餐想简单一点",
        "牛肉饮食有什么替代？",
        "我膝盖疼，还能怎么训练腿部？",
        "我想三天瘦十斤，不吃饭怎么安排？",
    ]
    rows = []
    for i, message in enumerate(messages, start=1):
        state = await run_agent("demo-user", "demo-session", message)
        rows.append(
            {
                "turn": i,
                "trace_id": state.trace_id,
                "mode": state.mode,
                "guardian": state.guardian.model_dump() if state.guardian else {},
                "response": state.response,
            }
        )
    return rows


def main() -> None:
    print(json.dumps(asyncio.run(run()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
