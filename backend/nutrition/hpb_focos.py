from __future__ import annotations

import json
from datetime import UTC, datetime

from backend.nutrition.schemas import NutritionResult
from backend.runtime.config import ROOT_DIR


def load_hpb_cache() -> list[dict]:
    path = ROOT_DIR / "data/hpb_focos_cache.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def search_hpb_cache(query: str) -> NutritionResult | None:
    q = query.strip().lower()
    for item in load_hpb_cache():
        aliases = [item["name"], *item.get("aliases", [])]
        if any(alias.lower() in q or q in alias.lower() for alias in aliases):
            return NutritionResult(
                name=item["name"],
                kcal=float(item["kcal"]),
                protein_g=float(item["protein_g"]),
                carb_g=float(item["carb_g"]),
                fat_g=float(item["fat_g"]),
                serving_size_g=float(item.get("serving_size_g", 100)),
                source="hpb_focos_cached_manual",
                source_detail=item.get("source_detail"),
                fetched_at=item.get("fetched_or_exported_at") or datetime.now(UTC).isoformat(),
                fallback_used=True,
                fallback_from=["openfoodfacts", "usda"],
                fallback_to="hpb_focos_cached_manual",
                fallback_reason="no_match",
                raw=item,
            )
    return None
