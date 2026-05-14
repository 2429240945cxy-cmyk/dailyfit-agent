from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    target = ROOT / "data/usda_sr_legacy/snapshot_manifest.json"
    payload = {
        "source": "USDA FoodData Central SR Legacy",
        "source_url": "https://fdc.nal.usda.gov/",
        "created_for": "DailyFit Agent compact benchmark construction",
        "note": "The nutrition_v2 builder uses documented public nutrition values; no LLM generated ground truth.",
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"written": str(target)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
