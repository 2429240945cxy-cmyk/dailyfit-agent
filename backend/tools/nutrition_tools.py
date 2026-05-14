from __future__ import annotations

from backend.nutrition.calculator import scale_serving
from backend.nutrition.hpb_focos import search_hpb_cache
from backend.nutrition.local_food_db import search_local_food
from backend.nutrition.openfoodfacts import search_openfoodfacts
from backend.nutrition.schemas import NutritionResult
from backend.nutrition.usda import search_usda
from backend.runtime.config import get_settings


async def lookup_nutrition(query: str, serving_size_g: float | None = None) -> NutritionResult:
    settings = get_settings()
    if settings.mode == "demo_mock":
        result = search_local_food(query, fallback=False)
        if result is None:
            result = search_local_food("oatmeal", fallback=False)
            assert result is not None
            result.fallback_used = True
            result.fallback_from = ["demo_query"]
            result.fallback_to = "local_food_db"
            result.fallback_reason = "no_match"
        return scale_serving(result, serving_size_g)

    errors: list[str] = []
    try:
        return scale_serving(await search_openfoodfacts(query), serving_size_g)
    except Exception as exc:
        errors.append(f"openfoodfacts:{type(exc).__name__}:{exc}")
    try:
        return scale_serving(await search_usda(query), serving_size_g)
    except Exception as exc:
        errors.append(f"usda:{type(exc).__name__}:{exc}")

    hpb = search_hpb_cache(query)
    if hpb:
        hpb.fallback_reason = "no_match"
        hpb.raw = {"source_errors": errors, "hpb": hpb.raw}
        return scale_serving(hpb, serving_size_g)

    local = search_local_food(query, fallback=True, reason="no_match")
    if local:
        local.raw = {"source_errors": errors, "local": local.raw}
        return scale_serving(local, serving_size_g)

    fallback = search_local_food("oatmeal", fallback=True, reason="no_match")
    assert fallback is not None
    fallback.raw = {"source_errors": errors, "forced_demo_fallback": True}
    return scale_serving(fallback, serving_size_g)
