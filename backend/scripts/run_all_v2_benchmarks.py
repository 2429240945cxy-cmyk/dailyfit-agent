from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.scripts.build_e2e_v2_dataset import main as build_e2e
from backend.scripts.build_guardian_v2_dataset import main as build_guardian
from backend.scripts.build_memory_v2_dataset import main as build_memory
from backend.scripts.build_nutrition_v2_dataset import main as build_nutrition
from backend.scripts.run_e2e_benchmark import run as run_e2e
from backend.scripts.run_guardian_benchmark import run as run_guardian
from backend.scripts.run_memory_benchmark import run as run_memory
from backend.scripts.run_nutrition_benchmark import run as run_nutrition


async def run_all() -> list[dict]:
    build_nutrition()
    build_guardian()
    build_memory()
    build_e2e()
    return [await run_nutrition(), run_guardian(), run_memory(), await run_e2e()]


def main() -> None:
    print(json.dumps(asyncio.run(run_all()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
