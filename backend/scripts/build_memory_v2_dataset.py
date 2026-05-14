from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "evals/datasets/memory_v2.jsonl"


MEMORIES = [
    ("mem_beef", "用户不吃牛肉"),
    ("mem_lactose", "用户乳糖不耐"),
    ("mem_cut", "用户目标是减脂"),
    ("mem_bulk", "用户目标改为增肌"),
    ("mem_knee", "用户有膝盖疼痛"),
    ("mem_breakfast", "用户喜欢简单早餐"),
    ("mem_budget", "用户预算低"),
    ("mem_chinese", "用户喜欢中餐"),
    ("mem_marathon", "用户在准备马拉松"),
    ("mem_shoulder", "用户有肩伤"),
]


def main() -> None:
    samples = [
        ("牛肉饮食有什么替代", ["mem_beef"], True, "paraphrase"),
        ("别给我乳制品", ["mem_lactose"], True, "constraint"),
        ("还按减脂目标做早餐", ["mem_cut"], True, "long_gap"),
        ("现在改成增肌了", ["mem_bulk"], True, "changed_goal"),
        ("腿部训练避开膝盖压力", ["mem_knee"], True, "constraint"),
        ("明早要快手一点", ["mem_breakfast"], True, "preference"),
        ("便宜高蛋白怎么吃", ["mem_budget"], True, "preference"),
        ("想吃中餐风格", ["mem_chinese"], True, "preference"),
        ("长跑前一天怎么补碳", ["mem_marathon"], True, "long_gap"),
        ("肩伤不能推举", ["mem_shoulder"], True, "constraint"),
        ("牛排推荐", ["mem_beef"], True, "paraphrase"),
        ("milk-free smoothie", ["mem_lactose"], True, "paraphrase"),
        ("cutting meal prep", ["mem_cut"], True, "paraphrase"),
        ("bulk diet now", ["mem_bulk"], True, "changed_goal"),
        ("knee-friendly lower body", ["mem_knee"], True, "paraphrase"),
        ("simple breakfast", ["mem_breakfast"], True, "paraphrase"),
        ("low budget dinner", ["mem_budget"], True, "paraphrase"),
        ("Chinese-style lunch", ["mem_chinese"], True, "paraphrase"),
        ("marathon carb loading", ["mem_marathon"], True, "paraphrase"),
        ("shoulder safe workout", ["mem_shoulder"], True, "paraphrase"),
        ("我今天想吃鱼", [], False, "false_positive"),
        ("帮我查香蕉营养", [], False, "false_positive"),
        ("今天几点训练", [], False, "false_positive"),
        ("水喝多少", [], False, "false_positive"),
        ("鸡蛋有多少蛋白", [], False, "false_positive"),
        ("三个月后继续按不吃牛肉安排", ["mem_beef"], True, "long_gap"),
        ("预算还是很紧", ["mem_budget"], True, "long_gap"),
        ("从减脂切换到维持", ["mem_cut"], True, "profile_update"),
        ("早餐还是越简单越好", ["mem_breakfast"], True, "long_gap"),
        ("膝盖最近好了但先保守", ["mem_knee"], True, "profile_update"),
    ]
    rows = []
    for idx, (query, expected, should_hit, category) in enumerate(samples, start=1):
        rows.append(
            {
                "id": f"m_{idx:03d}",
                "conversation_id": f"conv_{(idx - 1) // 5 + 1}",
                "turn_id": f"t_{idx}",
                "query": query,
                "expected_memory_ids": expected,
                "should_hit": should_hit,
                "category": category,
            }
        )
    TARGET.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    print(json.dumps({"dataset": str(TARGET), "rows": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
