from backend.graph.state import AgentState
from backend.guardian.schemas import GuardianVerdict
from backend.nutrition.schemas import NutritionResult
from backend.workout.schemas import Exercise


def test_guardian_schema() -> None:
    verdict = GuardianVerdict(verdict="warn", risk_categories=["injury_training"], reason="careful")
    assert verdict.verdict == "warn"
    assert verdict.confidence <= 1


def test_nutrition_schema() -> None:
    result = NutritionResult(
        name="oats",
        kcal=389,
        protein_g=16.9,
        carb_g=66.3,
        fat_g=6.9,
        serving_size_g=100,
        source="local_food_db",
    )
    assert result.source == "local_food_db"


def test_workout_schema() -> None:
    exercise = Exercise(name="Push Up", primaryMuscles=["chest"])
    assert exercise.primaryMuscles == ["chest"]


def test_agent_state_schema() -> None:
    state = AgentState(user_id="u1", session_id="s1", message="hi", trace_id="tr_test")
    assert state.mode == "demo_mock"
