from __future__ import annotations

from backend.workout.contraindication_rules import filter_contraindicated
from backend.workout.exercise_db import load_exercises
from backend.workout.schemas import WorkoutPlan


def build_workout_plan(goal: str, constraints: list[str] | None = None, limit: int = 5) -> WorkoutPlan:
    constraints = constraints or []
    exercises, fallback_used, fallback_reason = load_exercises()
    level_order = {"beginner": 0, "intermediate": 1, "expert": 2}
    sorted_exercises = sorted(exercises, key=lambda ex: level_order.get((ex.level or "").lower(), 9))
    kept, excluded = filter_contraindicated(sorted_exercises, constraints, limit=limit)
    return WorkoutPlan(
        goal=goal,
        constraints=constraints,
        exercises=kept,
        excluded=excluded[:20],
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )
