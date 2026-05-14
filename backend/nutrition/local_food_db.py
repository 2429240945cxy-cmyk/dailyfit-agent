from __future__ import annotations

import json
from datetime import UTC, datetime

from backend.nutrition.schemas import NutritionResult
from backend.runtime.config import ROOT_DIR


def _norm(text: str) -> str:
    return text.strip().lower().replace("，", ",")


def load_local_foods() -> list[dict]:
    path = ROOT_DIR / "data/sample_foods.json"
    return json.loads(path.read_text(encoding="utf-8"))


def search_local_food(query: str, fallback: bool = True, reason: str = "no_match") -> NutritionResult | None:
    q = _norm(query)
    foods = load_local_foods()
    best: dict | None = None
    for food in foods:
        aliases = [food["name"], *food.get("aliases", [])]
        if any(_norm(alias) in q or q in _norm(alias) for alias in aliases):
            best = food
            break
    if best is None:
        return None
    return NutritionResult(
        name=best["name"],
        kcal=float(best["kcal"]),
        protein_g=float(best["protein_g"]),
        carb_g=float(best["carb_g"]),
        fat_g=float(best["fat_g"]),
        serving_size_g=float(best.get("serving_size_g", 100)),
        source="local_food_db",
        source_detail=best.get("source_detail"),
        fetched_at=datetime.now(UTC).isoformat(),
        fallback_used=fallback,
        fallback_from=["openfoodfacts", "usda"],
        fallback_to="local_food_db" if fallback else None,
        fallback_reason=reason if fallback else None,
        raw={"aliases": best.get("aliases", [])},
    )
