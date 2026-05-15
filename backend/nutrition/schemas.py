from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

NutritionSource = Literal[
    "openfoodfacts",
    "usda_fdc",
    "usda_sr_legacy_cache",
    "hpb_focos_cached_manual",
    "local_food_db",
    "computed",
]


class NutritionResult(BaseModel):
    name: str
    kcal: float
    protein_g: float
    carb_g: float
    fat_g: float
    serving_size_g: float | None = None
    source: NutritionSource
    source_url: str | None = None
    source_detail: str | None = None
    fetched_at: str | None = None
    fallback_used: bool = False
    fallback_from: list[str] = []
    fallback_to: str | None = None
    fallback_reason: str | None = None
    raw: dict | None = None


class NutritionLookupRequest(BaseModel):
    query: str
    mode: str = "demo_mock"
    serving_size_g: float | None = None
