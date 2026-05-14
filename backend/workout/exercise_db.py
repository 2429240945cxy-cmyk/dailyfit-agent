from __future__ import annotations

import json
from pathlib import Path

from backend.runtime.config import ROOT_DIR
from backend.workout.schemas import Exercise

EXERCISE_DB_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"


def load_exercises(path: Path | None = None) -> tuple[list[Exercise], bool, str | None]:
    db_path = path or (ROOT_DIR / "data/exercises_db.json")
    fallback = False
    reason = None
    if not db_path.exists():
        db_path = ROOT_DIR / "data/sample_exercises.json"
        fallback = True
        reason = "missing_exercise_db"
    rows = json.loads(db_path.read_text(encoding="utf-8"))
    exercises = [Exercise(**row) for row in rows]
    return exercises, fallback, reason


def exercise_count(path: Path | None = None) -> int:
    exercises, _, _ = load_exercises(path)
    return len(exercises)
