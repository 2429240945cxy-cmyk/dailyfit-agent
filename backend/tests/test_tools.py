import pytest

from backend.tools.nutrition_tools import lookup_nutrition
from backend.tools.profile_tools import update_profile_from_message
from backend.tools.workout_tools import plan_workout


@pytest.mark.asyncio
async def test_nutrition_tool(monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "demo_mock")
    result = await lookup_nutrition("香蕉")
    assert result.kcal == 89


def test_workout_tool() -> None:
    plan = plan_workout("strength", ["knee pain"])
    assert plan.exercises


def test_profile_tool(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_DB_PATH", str(tmp_path / "mem.db"))
    created = update_profile_from_message("u1", "我不吃牛肉")
    assert created
