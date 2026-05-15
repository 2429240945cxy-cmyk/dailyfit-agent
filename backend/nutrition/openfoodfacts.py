from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

import httpx

from backend.nutrition.errors import NutritionParseError
from backend.nutrition.schemas import NutritionResult

OFF_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/search"


def _nutriment(nutriments: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = nutriments.get(key)
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
    return None


async def search_openfoodfacts(query: str, timeout: float = 5.0) -> NutritionResult:
    params = {
        "search_terms": query,
        "page_size": 1,
        "fields": "product_name,nutriments,code,url,brands",
    }
    headers = {"User-Agent": "DailyFitAgent/1.0 (portfolio demo)"}
    last_error: Exception | None = None
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        for _ in range(3):
            try:
                response = await client.get(OFF_SEARCH_URL, params=params)
                if response.status_code == 429:
                    raise httpx.HTTPStatusError("rate_limited", request=response.request, response=response)
                response.raise_for_status()
                payload = response.json()
                products = payload.get("products") or []
                if not products:
                    raise NutritionParseError("no_match")
                product = products[0]
                product_name = product.get("product_name") or query
                query_terms = [term for term in re.findall(r"[a-zA-Z]{3,}", query.lower()) if term not in {"and", "the"}]
                if query_terms and not any(term in product_name.lower() for term in query_terms):
                    raise NutritionParseError("no_match")
                nutriments = product.get("nutriments") or {}
                kcal = _nutriment(nutriments, "energy-kcal_100g", "energy-kcal")
                protein = _nutriment(nutriments, "proteins_100g", "proteins")
                carbs = _nutriment(nutriments, "carbohydrates_100g", "carbohydrates")
                fat = _nutriment(nutriments, "fat_100g", "fat")
                if None in {kcal, protein, carbs, fat}:
                    raise NutritionParseError("parse_error")
                return NutritionResult(
                    name=product_name,
                    kcal=kcal or 0.0,
                    protein_g=protein or 0.0,
                    carb_g=carbs or 0.0,
                    fat_g=fat or 0.0,
                    serving_size_g=100,
                    source="openfoodfacts",
                    source_url=product.get("url")
                    or f"https://world.openfoodfacts.org/product/{product.get('code', '')}",
                    source_detail="Open Food Facts API v2 search result per 100g.",
                    fetched_at=datetime.now(UTC).isoformat(),
                    fallback_used=False,
                    raw=product,
                )
            except Exception as exc:
                last_error = exc
    raise NutritionParseError(str(last_error or "openfoodfacts_failed"))
