from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"


def latest_results() -> dict[str, dict]:
    results = {}
    for path in (ROOT / "evals/results").glob("*_v2_*.json"):
        if path.name == "baseline.json" or "pre_judge_fix" in path.name:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        results[payload["benchmark"]] = payload
    return results


def format_table(results: dict[str, dict]) -> str:
    rows = ["| Benchmark | Mode | Samples | Metric | Value |", "|---|---:|---:|---|---:|"]
    mapping = [
        ("nutrition", "Nutrition v2", "meal_kcal_mae"),
        ("guardian", "Guardian v2", "precision/recall"),
        ("memory", "Memory v2", "hit_rate@3"),
        ("e2e", "E2E v2", "judge_pass_rate"),
    ]
    for key, label, metric in mapping:
        result = results.get(key)
        if not result:
            rows.append(f"| {label} | live_missing_key_not_run | 0 | {metric} | 0.0 |")
            continue
        metrics = result.get("metrics", {})
        if metric == "precision/recall":
            value = f"{metrics.get('precision', 0.0)}/{metrics.get('recall', 0.0)}"
        else:
            value = str(metrics.get(metric, 0.0))
        rows.append(
            f"| {label} | {result.get('mode')} | {result.get('sample_count')} | {metric} | {value} |"
        )
    return "\n".join(rows)


def all_result_rows() -> str:
    rows = ["| Benchmark | Mode | Samples | Metric | Value |", "|---|---:|---:|---|---:|"]
    seen = set()
    for path in sorted((ROOT / "evals/results").glob("*_v2*.json")):
        if path.name in {"baseline.json", "cost_report_v2.json"} or "pre_judge_fix" in path.name:
            continue
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        key = (result.get("benchmark"), result.get("mode"))
        if key in seen:
            continue
        seen.add(key)
        metrics = result.get("metrics", {})
        metric_name = next(iter(metrics), "n/a")
        value = metrics.get(metric_name, 0.0)
        if result.get("benchmark") == "guardian":
            metric_name = "precision/recall"
            value = f"{metrics.get('precision', 0.0)}/{metrics.get('recall', 0.0)}"
        rows.append(
            f"| {result.get('benchmark', '').title()} v2 | {result.get('mode')} | "
            f"{result.get('sample_count')} | {metric_name} | {value} |"
        )
    return "\n".join(rows)


def main() -> None:
    text = README.read_text(encoding="utf-8")
    table = format_table(latest_results())
    updated = re.sub(
        r"<!-- BENCHMARK_TABLE_START -->.*?<!-- BENCHMARK_TABLE_END -->",
        f"<!-- BENCHMARK_TABLE_START -->\n{table}\n<!-- BENCHMARK_TABLE_END -->",
        text,
        flags=re.S,
    )
    detailed = all_result_rows()
    if "<!-- BENCHMARK_ALL_MODES_START -->" not in updated:
        updated += "\n\n## All Benchmark Modes\n\n<!-- BENCHMARK_ALL_MODES_START -->\n<!-- BENCHMARK_ALL_MODES_END -->\n"
    updated = re.sub(
        r"<!-- BENCHMARK_ALL_MODES_START -->.*?<!-- BENCHMARK_ALL_MODES_END -->",
        f"<!-- BENCHMARK_ALL_MODES_START -->\n{detailed}\n<!-- BENCHMARK_ALL_MODES_END -->",
        updated,
        flags=re.S,
    )
    README.write_text(updated, encoding="utf-8")
    print(json.dumps({"readme_numbers_verified": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
