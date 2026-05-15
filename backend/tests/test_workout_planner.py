from backend.workout.contraindication_rules import exclusion_reason
from backend.workout.planner import build_workout_plan
from backend.workout.schemas import Exercise


def test_knee_rule_excludes_jump() -> None:
    exercise = Exercise(name="Box Jump", primaryMuscles=["quadriceps"], equipment="body only")
    assert exclusion_reason(exercise, ["knee pain"]) is not None


def test_knee_rule_excludes_air_bike_from_plan() -> None:
    plan = build_workout_plan("腿部训练", ["knee pain"], limit=8)
    names = [item.name.lower() for item in plan.exercises]
    assert not any("air bike" in name for name in names)
    assert not any("squat" in name or "lunge" in name for name in names)
    assert not any("skip" in name or "bound" in name or "skating" in name for name in names)
    assert not any("step" in name or "stairs" in name or "yoke" in name or "atlas" in name for name in names)
    assert not any("sprint" in name or "crawl" in name or "sled" in name for name in names)


def test_workout_plan_returns_exercises() -> None:
    plan = build_workout_plan("beginner strength", ["knee pain"], limit=2)
    assert len(plan.exercises) > 0
