from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_result(name: str, result: dict) -> Path:
    result_dir = ROOT / "evals/results"
    result_dir.mkdir(parents=True, exist_ok=True)
    mode = result.get("mode", "demo_mock")
    path = result_dir / f"{name}_v2_{mode}.json"
    result["created_at"] = result.get("created_at") or datetime.now(UTC).isoformat()
    content = json.dumps(result, ensure_ascii=False, indent=2)
    path.write_text(content, encoding="utf-8")
    canonical = result_dir / f"{name}_v2.json"
    canonical.write_text(content, encoding="utf-8")
    return path


def base_result(benchmark: str, dataset: str, mode: str, sample_count: int) -> dict:
    return {
        "benchmark": benchmark,
        "dataset": dataset,
        "mode": mode,
        "sample_count": sample_count,
        "metrics": {},
        "cost_usd": 0.0,
        "cache_hit_rate": 0.0,
        "fallback_count": 0,
        "provider": "aliyun_openai",
        "model": "qwen-plus",
        "judge_model": "qwen-max",
        "created_at": datetime.now(UTC).isoformat(),
        "notes": [],
    }
