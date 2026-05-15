from __future__ import annotations

from backend.workout.contraindication_rules import filter_contraindicated
from backend.workout.exercise_db import load_exercises
from backend.workout.schemas import Exercise, WorkoutPlan


def _goal_relevance(exercise: Exercise, goal: str) -> int:
    lowered = goal.lower()
    muscles = {muscle.lower() for muscle in [*exercise.primaryMuscles, *exercise.secondaryMuscles]}
    if any(term in lowered for term in ["腿", "leg", "lower body"]):
        return len(muscles & {"hamstrings", "glutes", "calves", "adductors", "abductors"})
    if any(term in lowered for term in ["上肢", "upper", "手臂", "arm"]):
        return len(muscles & {"biceps", "triceps", "chest", "lats", "middle back", "forearms"})
    if any(term in lowered for term in ["核心", "core", "腹"]):
        return len(muscles & {"abdominals"})
    return 0


def build_workout_plan(goal: str, constraints: list[str] | None = None, limit: int = 5) -> WorkoutPlan:
    constraints = constraints or []
    exercises, fallback_used, fallback_reason = load_exercises()
    level_order = {"beginner": 0, "intermediate": 1, "expert": 2}
    sorted_exercises = sorted(
        exercises,
        key=lambda ex: (-_goal_relevance(ex, goal), level_order.get((ex.level or "").lower(), 9)),
    )
    kept, excluded = filter_contraindicated(sorted_exercises, constraints, limit=limit)
    return WorkoutPlan(
        goal=goal,
        constraints=constraints,
        exercises=kept,
        excluded=excluded[:20],
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )
