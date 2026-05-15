from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.runtime.config import get_settings
from backend.scripts.benchmark_common import base_result, read_jsonl, write_result
from backend.tools.nutrition_tools import lookup_nutrition


async def run() -> dict:
    path = ROOT / "evals/datasets/nutrition_v2.jsonl"
    if not path.exists():
        from backend.scripts.build_nutrition_v2_dataset import main as build

        build()
    rows = read_jsonl(path)
    settings = get_settings()
    mode = settings.public_mode
    errors = []
    fallback_count = 0
    real_source_count = 0
    hits = 0
    adversarial_hits = 0
    adversarial_count = 0
    for row in rows:
        gt = row["ground_truth"]
        result = await lookup_nutrition(row["query"])
        error = abs(result.kcal - float(gt["kcal"]))
        errors.append(error)
        if result.fallback_used:
            fallback_count += 1
        computed_from = (result.raw or {}).get("computed_from_source") if result.raw else None
        if result.source in {"openfoodfacts", "usda_fdc", "usda_sr_legacy_cache"} or computed_from in {
            "openfoodfacts",
            "usda_fdc",
            "usda_sr_legacy_cache",
        }:
            real_source_count += 1
        if error <= 120:
            hits += 1
            if row["category"] != "standard":
                adversarial_hits += 1
        if row["category"] != "standard":
            adversarial_count += 1
    output = base_result("nutrition", str(path), mode, len(rows))
    output["metrics"] = {
        "meal_kcal_mae": round(sum(errors) / max(1, len(errors)), 2),
        "food_lookup_hit_rate": round(hits / max(1, len(rows)), 4),
        "adversarial_hit_rate": round(adversarial_hits / max(1, adversarial_count), 4),
        "real_source_rate": round(real_source_count / max(1, len(rows)), 4),
    }
    output["fallback_count"] = fallback_count
    output["notes"].append("Ground truth is independent of runtime lookup responses.")
    write_result("nutrition", output)
    return output


def main() -> None:
    print(json.dumps(asyncio.run(run()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
