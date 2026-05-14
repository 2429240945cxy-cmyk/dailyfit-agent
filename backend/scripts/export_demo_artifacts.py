from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.scripts.run_demo import run


def main() -> None:
    target = ROOT / "demo/expected_outputs/demo_outputs.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asyncio.run(run()), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"written": str(target)}))


if __name__ == "__main__":
    main()
