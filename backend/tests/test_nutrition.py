import pytest

from backend.nutrition.local_food_db import search_local_food
from backend.tools.nutrition_tools import lookup_nutrition


def test_local_food_lookup_chinese_oats() -> None:
    result = search_local_food("燕麦片 100g", fallback=False)
    assert result is not None
    assert result.kcal == 389
    assert result.source == "local_food_db"


@pytest.mark.asyncio
async def test_demo_lookup_has_mode_safe_fallback(monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "demo_mock")
    result = await lookup_nutrition("unknown food")
    assert result.source == "local_food_db"
    assert result.fallback_used is True
