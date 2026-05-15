import pytest

from backend.nutrition.hpb_focos import search_hpb_cache
from backend.nutrition.openfoodfacts import _nutriment
from backend.nutrition.usda import _extract_nutrients


def test_openfoodfacts_nutriment_parser() -> None:
    assert _nutriment({"energy-kcal_100g": "123.5"}, "energy-kcal_100g") == 123.5


def test_usda_nutrient_parser() -> None:
    food = {
        "foodNutrients": [
            {"nutrientId": 1008, "value": 130},
            {"nutrientId": 1003, "value": 2.7},
            {"nutrientId": 1005, "value": 28.2},
            {"nutrientId": 1004, "value": 0.3},
        ]
    }
    assert _extract_nutrients(food)["kcal"] == 130


def test_hpb_cache_is_manual_cached_source() -> None:
    result = search_hpb_cache("炒河粉")
    assert result is not None
    assert result.source == "hpb_focos_cached_manual"
    assert result.fallback_used is True


@pytest.mark.asyncio
async def test_live_lookup_falls_back_without_keys(monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "live")
    monkeypatch.delenv("USDA_API_KEY", raising=False)
    from backend.tools.nutrition_tools import lookup_nutrition

    result = await lookup_nutrition("燕麦")
    assert result.source in {
        "openfoodfacts",
        "usda_fdc",
        "usda_sr_legacy_cache",
        "hpb_focos_cached_manual",
        "local_food_db",
    }
