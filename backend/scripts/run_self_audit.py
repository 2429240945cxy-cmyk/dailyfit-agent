from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.runtime.github_client import GitHubClient

PROTECTED = {
    ".env",
    "evals/datasets/nutrition_v2.jsonl",
    "evals/datasets/guardian_v2.jsonl",
    "evals/datasets/memory_v2.jsonl",
    "evals/datasets/e2e_v2.jsonl",
    "docs/dataset_construction.md",
}


def run_cmd(args: list[str]) -> dict:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "cmd": args,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-1200:],
        "stderr_tail": result.stderr[-1200:],
    }


def detect_regressions() -> list[dict]:
    baseline_path = ROOT / "evals/results/baseline.json"
    if not baseline_path.exists():
        return []
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [{"benchmark": "baseline", "reason": "parse_error"}]
    regressions = []
    for result_path in (ROOT / "evals/results").glob("*_v2_*.json"):
        if result_path.name == "baseline.json" or "pre_judge_fix" in result_path.name:
            continue
        current = json.loads(result_path.read_text(encoding="utf-8"))
        old = baseline.get(current.get("benchmark"))
        if not old:
            continue
        name = current["benchmark"]
        if name == "guardian":
            old_recall = old.get("metrics", {}).get("recall", 0)
            new_recall = current.get("metrics", {}).get("recall", 0)
            if old_recall - new_recall > 0.05:
                regressions.append({"benchmark": name, "old": old_recall, "new": new_recall})
        if name == "memory":
            old_hit = old.get("metrics", {}).get("hit_rate@3", 0)
            new_hit = current.get("metrics", {}).get("hit_rate@3", 0)
            if old_hit - new_hit > 0.05:
                regressions.append({"benchmark": name, "old": old_hit, "new": new_hit})
        if name == "e2e" and current.get("metrics", {}).get("judge_error_count", 0) > 0:
            regressions.append({"benchmark": name, "reason": "judge_error_count"})
    return regressions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-issues", action="store_true")
    args = parser.parse_args()
    commands = [
        [sys.executable, "-m", "pytest", "backend/tests/", "-q"],
        [sys.executable, "backend/scripts/run_all_v2_benchmarks.py"],
        [sys.executable, "backend/scripts/scan_sensitive_tokens.py"],
        [sys.executable, "backend/scripts/verify_readme_numbers.py"],
    ]
    results = [run_cmd(cmd) for cmd in commands]
    regressions = detect_regressions()
    failures = [result for result in results if result["returncode"] != 0]
    if args.create_issues and (regressions or failures):
        client = GitHubClient()
        body = json.dumps({"regressions": regressions, "failures": failures}, ensure_ascii=False, indent=2)
        client.create_issue("Self-audit regression or failure", body, labels=["self-audit"])
    output = {
        "self_audit_completed": not failures,
        "regressions_detected": len(regressions),
        "failures": failures,
        "mode": "dry_run" if args.dry_run else "active",
        "protected_files": sorted(PROTECTED),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
