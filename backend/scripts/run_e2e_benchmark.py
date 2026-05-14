from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.graph.workflow import run_agent
from backend.runtime.config import get_settings
from backend.runtime.llm import get_judge_client
from backend.scripts.benchmark_common import base_result, read_jsonl, write_result


async def judge_response(sample: dict, transcript: list[dict]) -> tuple[bool, dict]:
    settings = get_settings()
    if settings.mode != "live":
        return True, {"judge_mode": "demo_mock", "score": 0.8}
    if settings.judge_model == settings.llm_model:
        return False, {"error": "judge model must differ", "judge_model": settings.judge_model}
    if not settings.dashscope_api_key_present:
        return False, {"error": "DASHSCOPE_API_KEY missing"}
    client = get_judge_client()
    prompt = {
        "sample": sample,
        "transcript": transcript,
        "instruction": "Return JSON {passed: boolean, score: number, notes: string[]}.",
    }
    response = await client.generate(
        [{"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
        temperature=0.0,
        purpose="judge",
    )
    if response.error or response.input_tokens + response.output_tokens <= 0:
        return False, {"error": response.error or "zero usage"}
    try:
        payload = json.loads(response.content)
    except json.JSONDecodeError:
        payload = {"passed": False, "score": 0, "notes": ["parse_error"]}
    return bool(payload.get("passed")), payload


async def run() -> dict:
    path = ROOT / "evals/datasets/e2e_v2.jsonl"
    if not path.exists():
        from backend.scripts.build_e2e_v2_dataset import main as build

        build()
    rows = read_jsonl(path)
    settings = get_settings()
    pass_count = 0
    judge_errors = 0
    trace_path = ROOT / "evals/results/e2e_v2_judge_traces.jsonl"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_lines = []
    for row in rows:
        transcript = []
        session_id = f"bench-{row['id']}"
        for turn in row["turns"]:
            state = await run_agent("bench-user", session_id, turn["content"])
            transcript.append(
                {
                    "user": turn["content"],
                    "assistant": state.response,
                    "trace_id": state.trace_id,
                    "guardian": state.guardian.model_dump() if state.guardian else {},
                    "mode": state.mode,
                }
            )
        passed, judge_payload = await judge_response(row, transcript)
        if passed:
            pass_count += 1
        if "error" in judge_payload:
            judge_errors += 1
        trace_lines.append(
            json.dumps(
                {"id": row["id"], "passed": passed, "judge": judge_payload, "transcript": transcript},
                ensure_ascii=False,
            )
        )
    trace_path.write_text("\n".join(trace_lines) + "\n", encoding="utf-8")
    mode = settings.public_mode
    if settings.mode == "live" and not settings.dashscope_api_key_present:
        mode = "live_missing_key_not_run"
    output = base_result("e2e", str(path), mode, len(rows))
    output["metrics"] = {
        "judge_pass_rate": round(pass_count / max(1, len(rows)), 4),
        "judge_error_count": judge_errors,
    }
    if settings.mode == "live" and settings.judge_model == settings.llm_model:
        output["notes"].append("E2E live judge failed: judge model must differ from tested model.")
    write_result("e2e", output)
    return output


def main() -> None:
    print(json.dumps(asyncio.run(run()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
