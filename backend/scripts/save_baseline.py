from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    result_dir = ROOT / "evals/results"
    latest = {}
    for path in result_dir.glob("*_v2_*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        latest[payload["benchmark"]] = payload
    target = result_dir / "baseline.json"
    target.write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"baseline": str(target), "benchmarks": sorted(latest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
