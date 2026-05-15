from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.runtime.llm_usage import UsageStore


def main() -> None:
    summary = UsageStore().today_summary()
    result_path = ROOT / "evals/results/cost_report_v2.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    target = ROOT / "docs/cost_report.md"
    text = (
        "# Cost Report\n\n"
        f"- Date: {summary['date']}\n"
        f"- Input tokens: {summary['input_tokens']}\n"
        f"- Output tokens: {summary['output_tokens']}\n"
        f"- Total live cost USD: {summary['cost_usd']:.6f}\n"
        f"- Cache hit rate: {summary['cache_hit_rate']:.4f}\n"
        f"- Calls: {summary['call_count']}\n"
    )
    target.write_text(text, encoding="utf-8")
    print(json.dumps({"written": str(target), **summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
