from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from typing import Any

import httpx

from backend.nutrition.errors import NutritionParseError
from backend.nutrition.schemas import NutritionResult

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


NUTRIENT_IDS = {
    "kcal": {1008, 2047, 2048},
    "protein_g": {1003},
    "fat_g": {1004},
    "carb_g": {1005},
}

PREFERRED_DATA_TYPES = ["SR Legacy", "Foundation"]


def _tokenize_query(text: str) -> set[str]:
    tokens = set()
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if token in {"and", "or", "the", "with", "raw", "cooked"}:
            continue
        tokens.add(token.rstrip("s"))
    return tokens


def _extract_nutrients(food: dict[str, Any]) -> dict[str, float]:
    values = {"kcal": None, "protein_g": None, "fat_g": None, "carb_g": None}
    for nutrient in food.get("foodNutrients") or []:
        nutrient_id = nutrient.get("nutrientId") or nutrient.get("nutrientNumber")
        try:
            nutrient_id = int(nutrient_id)
        except (TypeError, ValueError):
            continue
        value = nutrient.get("value")
        if value is None:
            continue
        for key, ids in NUTRIENT_IDS.items():
            if nutrient_id in ids and values[key] is None:
                values[key] = float(value)
    missing = [key for key, value in values.items() if value is None]
    if missing:
        raise NutritionParseError(f"missing nutrients: {missing}")
    return {key: float(value or 0.0) for key, value in values.items()}


async def search_usda(query: str, timeout: float = 5.0) -> NutritionResult:
    api_key = os.getenv("USDA_API_KEY") or "DEMO_KEY"
    params = {
        "api_key": api_key,
        "query": query,
        "dataType": PREFERRED_DATA_TYPES,
        "pageSize": 10,
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(USDA_SEARCH_URL, params=params)
        if response.status_code == 429:
            raise NutritionParseError("rate_limited")
        response.raise_for_status()
        payload = response.json()
    foods = payload.get("foods") or []
    if not foods:
        raise NutritionParseError("no_match")
    query_tokens = _tokenize_query(query)
    food = max(
        foods,
        key=lambda item: (
            len(query_tokens & _tokenize_query(item.get("description", ""))),
            1 if item.get("dataType") == "SR Legacy" else 0,
        ),
    )
    nutrients = _extract_nutrients(food)
    fdc_id = food.get("fdcId")
    return NutritionResult(
        name=food.get("description") or query,
        kcal=nutrients["kcal"],
        protein_g=nutrients["protein_g"],
        carb_g=nutrients["carb_g"],
        fat_g=nutrients["fat_g"],
        serving_size_g=100,
        source="usda_fdc",
        source_url=f"https://fdc.nal.usda.gov/fdc-app.html#/food-details/{fdc_id}/nutrients",
        source_detail=f"USDA FoodData Central {food.get('dataType', '')} fdc_id={fdc_id}",
        fetched_at=datetime.now(UTC).isoformat(),
        fallback_used=False,
        raw={
            "fdc_id": fdc_id,
            "dataType": food.get("dataType"),
            "description": food.get("description"),
            "api_key_mode": "configured" if os.getenv("USDA_API_KEY") else "public_demo_key",
        },
    )
