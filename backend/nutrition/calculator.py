from __future__ import annotations

from backend.nutrition.schemas import NutritionResult


def scale_serving(result: NutritionResult, serving_size_g: float | None) -> NutritionResult:
    if not serving_size_g or not result.serving_size_g:
        return result
    factor = serving_size_g / result.serving_size_g
    if abs(factor - 1.0) < 0.0001:
        return result
    data = result.model_dump()
    raw = dict(data.get("raw") or {})
    raw["computed_from_source"] = result.source
    data.update(
        {
            "kcal": round(result.kcal * factor, 2),
            "protein_g": round(result.protein_g * factor, 2),
            "carb_g": round(result.carb_g * factor, 2),
            "fat_g": round(result.fat_g * factor, 2),
            "serving_size_g": serving_size_g,
            "source": "computed" if result.source != "local_food_db" else result.source,
            "source_detail": f"{result.source_detail or result.source} scaled from per-100g reference.",
            "raw": raw,
        }
    )
    return NutritionResult(**data)
