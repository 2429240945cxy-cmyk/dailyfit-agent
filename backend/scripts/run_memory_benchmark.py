from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.memory.retrieval import search_memories
from backend.memory.schemas import MemoryItem
from backend.runtime.config import get_settings
from backend.scripts.benchmark_common import base_result, read_jsonl, write_result

MEMORY_BANK = {
    "mem_beef": "用户不吃牛肉",
    "mem_lactose": "用户乳糖不耐",
    "mem_cut": "用户目标是减脂",
    "mem_bulk": "用户目标改为增肌",
    "mem_knee": "用户有膝盖疼痛",
    "mem_breakfast": "用户喜欢简单早餐",
    "mem_budget": "用户预算低",
    "mem_chinese": "用户喜欢中餐",
    "mem_marathon": "用户在准备马拉松",
    "mem_shoulder": "用户有肩伤",
}


def run() -> dict:
    path = ROOT / "evals/datasets/memory_v2.jsonl"
    if not path.exists():
        from backend.scripts.build_memory_v2_dataset import main as build

        build()
    rows = read_jsonl(path)
    memories = [
        MemoryItem(
            id=key,
            user_id="bench",
            type="preference",
            summary=value,
            retrievable_text=value,
        )
        for key, value in MEMORY_BANK.items()
    ]
    correct = 0
    false_positive_ok = 0
    for row in rows:
        hits = search_memories(row["query"], memories, top_k=3)
        hit_ids = {hit.id for hit in hits}
        expected = set(row["expected_memory_ids"])
        if row["should_hit"] and expected & hit_ids:
            correct += 1
        if not row["should_hit"] and not hit_ids:
            false_positive_ok += 1
            correct += 1
    output = base_result("memory", str(path), get_settings().public_mode, len(rows))
    output["metrics"] = {
        "hit_rate@3": round(correct / max(1, len(rows)), 4),
        "false_positive_control": round(false_positive_ok / max(1, len([r for r in rows if not r["should_hit"]])), 4),
    }
    output["notes"].append("Memory queries use public/anonymized conversation patterns.")
    write_result("memory", output)
    return output


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
