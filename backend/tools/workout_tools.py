from __future__ import annotations

from backend.workout.planner import build_workout_plan
from backend.workout.schemas import WorkoutPlan


def plan_workout(goal: str, constraints: list[str] | None = None) -> WorkoutPlan:
    return build_workout_plan(goal, constraints or [])
