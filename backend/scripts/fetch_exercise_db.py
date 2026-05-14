from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import httpx

from backend.workout.exercise_db import EXERCISE_DB_URL


def main() -> None:
    target = ROOT / "data/exercises_db.json"
    try:
        response = httpx.get(EXERCISE_DB_URL, timeout=20.0)
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list) or len(rows) < 500:
            raise RuntimeError("downloaded exercise database too small")
        normalized = []
        for row in rows:
            normalized.append(
                {
                    "id": row.get("id") or row.get("name", "").replace(" ", "_"),
                    "name": row.get("name"),
                    "primaryMuscles": row.get("primaryMuscles") or [],
                    "secondaryMuscles": row.get("secondaryMuscles") or [],
                    "equipment": row.get("equipment"),
                    "level": row.get("level"),
                    "instructions": row.get("instructions") or [],
                    "images": row.get("images") or [],
                }
            )
        target.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"downloaded": True, "count": len(normalized), "target": str(target)}))
    except Exception as exc:
        sample = ROOT / "data/sample_exercises.json"
        target.write_text(sample.read_text(encoding="utf-8"), encoding="utf-8")
        print(
            json.dumps(
                {
                    "downloaded": False,
                    "fallback_used": True,
                    "fallback_from": ["free-exercise-db"],
                    "fallback_to": "data/sample_exercises.json",
                    "fallback_reason": type(exc).__name__,
                    "target": str(target),
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
