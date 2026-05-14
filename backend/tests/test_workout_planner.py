from backend.workout.contraindication_rules import exclusion_reason
from backend.workout.planner import build_workout_plan
from backend.workout.schemas import Exercise


def test_knee_rule_excludes_jump() -> None:
    exercise = Exercise(name="Box Jump", primaryMuscles=["quadriceps"], equipment="body only")
    assert exclusion_reason(exercise, ["knee pain"]) is not None


def test_workout_plan_returns_exercises() -> None:
    plan = build_workout_plan("beginner strength", ["knee pain"], limit=2)
    assert len(plan.exercises) > 0
