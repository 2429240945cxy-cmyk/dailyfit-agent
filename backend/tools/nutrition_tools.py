from __future__ import annotations

import re

from backend.nutrition.calculator import scale_serving
from backend.nutrition.hpb_focos import search_hpb_cache
from backend.nutrition.local_food_db import search_local_food
from backend.nutrition.openfoodfacts import search_openfoodfacts
from backend.nutrition.schemas import NutritionResult
from backend.nutrition.usda import search_usda
from backend.nutrition.usda_sr_cache import search_usda_sr_cache
from backend.nutrition.zh_en_dict import translate_food_query
from backend.runtime.config import get_settings


def _with_lookup_meta(
    result: NutritionResult,
    original_query: str,
    translated_query: str,
    was_translated: bool,
    matched_zh: str,
    source_errors: list[str] | None = None,
) -> NutritionResult:
    raw = dict(result.raw or {})
    raw["lookup_meta"] = {
        "original_query": original_query,
        "translated_query": translated_query if was_translated else None,
        "matched_zh_key": matched_zh or None,
        "source_errors": source_errors or [],
    }
    result.raw = raw
    return result


def _search_terms(query: str) -> tuple[list[str], str, bool, str]:
    translated_query, was_translated, matched_zh = translate_food_query(query)
    terms = [translated_query]
    if was_translated and translated_query != query:
        terms.append(query)
    return terms, translated_query, was_translated, matched_zh


def _infer_serving_size_g(query: str) -> float | None:
    lowered = query.lower()
    grams = re.search(r"(\d+(?:\.\d+)?)\s*g\b", lowered)
    if grams:
        return float(grams.group(1))
    if "one medium" in lowered and "banana" in lowered:
        return 118.0
    if "two large" in lowered and "egg" in lowered:
        return 100.0
    if "spoon" in lowered and "peanut" in lowered:
        return 16.0
    if "one bowl" in lowered and "rice" in lowered:
        return 200.0
    if "一碗" in query and "沙茶面" in query:
        return 400.0
    if "hawker plate" in lowered or "一盘" in query:
        return 400.0
    if "dessert serving" in lowered:
        return 150.0
    return None


async def lookup_nutrition(query: str, serving_size_g: float | None = None) -> NutritionResult:
    settings = get_settings()
    inferred_serving = serving_size_g if serving_size_g is not None else _infer_serving_size_g(query)
    if settings.mode == "demo_mock":
        result = search_local_food(query, fallback=False)
        if result is None:
            result = search_local_food("oatmeal", fallback=False)
            assert result is not None
            result.fallback_used = True
            result.fallback_from = ["demo_query"]
            result.fallback_to = "local_food_db"
            result.fallback_reason = "no_match"
        return scale_serving(result, inferred_serving)

    errors: list[str] = []
    terms, translated_query, was_translated, matched_zh = _search_terms(query)
    for term in terms:
        cached = search_usda_sr_cache(term)
        if cached is not None:
            return scale_serving(
                _with_lookup_meta(cached, query, translated_query, was_translated, matched_zh, errors),
                inferred_serving,
            )
        try:
            result = await search_usda(term)
            return scale_serving(
                _with_lookup_meta(result, query, translated_query, was_translated, matched_zh, errors),
                inferred_serving,
            )
        except Exception as exc:
            errors.append(f"usda:{type(exc).__name__}:{exc}")
        try:
            result = await search_openfoodfacts(term)
            return scale_serving(
                _with_lookup_meta(result, query, translated_query, was_translated, matched_zh, errors),
                inferred_serving,
            )
        except Exception as exc:
            errors.append(f"openfoodfacts:{type(exc).__name__}:{exc}")
        cached = search_usda_sr_cache(term, fallback_reason="live_source_unavailable")
        if cached is not None:
            return scale_serving(
                _with_lookup_meta(cached, query, translated_query, was_translated, matched_zh, errors),
                inferred_serving,
            )

    hpb = search_hpb_cache(query)
    if hpb:
        hpb.fallback_reason = "no_match"
        hpb.raw = {
            "source_errors": errors,
            "hpb": hpb.raw,
            "lookup_meta": {
                "original_query": query,
                "translated_query": translated_query if was_translated else None,
                "matched_zh_key": matched_zh or None,
            },
        }
        return scale_serving(hpb, inferred_serving)

    local = search_local_food(query, fallback=True, reason="no_match")
    if local is None and translated_query != query:
        local = search_local_food(translated_query, fallback=True, reason="no_match")
    if local:
        local.raw = {
            "source_errors": errors,
            "local": local.raw,
            "lookup_meta": {
                "original_query": query,
                "translated_query": translated_query if was_translated else None,
                "matched_zh_key": matched_zh or None,
            },
        }
        return scale_serving(local, inferred_serving)

    fallback = search_local_food("oatmeal", fallback=True, reason="no_match")
    assert fallback is not None
    fallback.raw = {
        "source_errors": errors,
        "forced_demo_fallback": True,
        "lookup_meta": {
            "original_query": query,
            "translated_query": translated_query if was_translated else None,
            "matched_zh_key": matched_zh or None,
        },
    }
    return scale_serving(fallback, inferred_serving)


async def search_food(query: str) -> dict:
    """Compatibility wrapper used by v6 smoke checks."""
    return (await lookup_nutrition(query)).model_dump()
