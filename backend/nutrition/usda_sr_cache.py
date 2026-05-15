from __future__ import annotations

from datetime import UTC, datetime

from backend.nutrition.schemas import NutritionResult

USDA_SR_CACHE: list[dict] = [
    {
        "name": "oats, rolled, raw",
        "aliases": ["oats", "oatmeal", "oats rolled raw", "oat meal", "oats dry"],
        "kcal": 389,
        "protein_g": 16.9,
        "carb_g": 66.3,
        "fat_g": 6.9,
    },
    {
        "name": "rice, white, cooked",
        "aliases": ["rice", "rice white cooked", "cooked rice", "one bowl rice", "rice cooked not raw"],
        "kcal": 130,
        "protein_g": 2.7,
        "carb_g": 28.2,
        "fat_g": 0.3,
    },
    {
        "name": "chicken breast, roasted",
        "aliases": ["chicken breast", "chicken breast roasted"],
        "kcal": 165,
        "protein_g": 31.0,
        "carb_g": 0.0,
        "fat_g": 3.6,
    },
    {
        "name": "egg, whole",
        "aliases": ["egg", "egg whole boiled", "egg two large"],
        "kcal": 143,
        "protein_g": 12.6,
        "carb_g": 0.7,
        "fat_g": 9.5,
    },
    {
        "name": "milk, whole",
        "aliases": ["milk", "milk whole"],
        "kcal": 61,
        "protein_g": 3.2,
        "carb_g": 4.8,
        "fat_g": 3.3,
    },
    {
        "name": "banana, raw",
        "aliases": ["banana", "banana raw", "banana one medium"],
        "kcal": 89,
        "protein_g": 1.1,
        "carb_g": 22.8,
        "fat_g": 0.3,
    },
    {
        "name": "broccoli, raw",
        "aliases": ["broccoli", "broccoli raw"],
        "kcal": 34,
        "protein_g": 2.8,
        "carb_g": 6.6,
        "fat_g": 0.4,
    },
    {
        "name": "salmon, atlantic, cooked",
        "aliases": ["salmon", "salmon atlantic cooked", "salmon sashimi"],
        "kcal": 206,
        "protein_g": 22.1,
        "carb_g": 0.0,
        "fat_g": 12.4,
    },
    {
        "name": "tofu, firm",
        "aliases": ["tofu", "tofu firm"],
        "kcal": 144,
        "protein_g": 17.3,
        "carb_g": 2.8,
        "fat_g": 8.7,
    },
    {
        "name": "beef, lean cooked",
        "aliases": ["beef", "beef ground lean cooked", "beef ground 90 lean cooked"],
        "kcal": 217,
        "protein_g": 26.1,
        "carb_g": 0.0,
        "fat_g": 11.8,
    },
    {
        "name": "pork, cooked lean",
        "aliases": ["pork", "pork loin lean cooked", "pork lean 100g cooked"],
        "kcal": 242,
        "protein_g": 27.3,
        "carb_g": 0.0,
        "fat_g": 13.9,
    },
    {
        "name": "sweet potato, baked",
        "aliases": ["sweet potato", "sweet potato baked"],
        "kcal": 86,
        "protein_g": 1.6,
        "carb_g": 20.1,
        "fat_g": 0.1,
    },
    {
        "name": "apple, raw, with skin",
        "aliases": ["apple", "apple raw with skin"],
        "kcal": 52,
        "protein_g": 0.3,
        "carb_g": 13.8,
        "fat_g": 0.2,
    },
    {
        "name": "peanut butter, smooth",
        "aliases": ["peanut butter", "peanut butter smooth"],
        "kcal": 588,
        "protein_g": 25.1,
        "carb_g": 20.0,
        "fat_g": 50.4,
    },
    {
        "name": "almonds, raw",
        "aliases": ["almonds", "almonds raw"],
        "kcal": 579,
        "protein_g": 21.2,
        "carb_g": 21.6,
        "fat_g": 49.9,
    },
    {
        "name": "greek yogurt, plain, nonfat",
        "aliases": ["greek yogurt", "yogurt greek plain nonfat"],
        "kcal": 59,
        "protein_g": 10.2,
        "carb_g": 3.6,
        "fat_g": 0.4,
    },
    {
        "name": "lentils, cooked",
        "aliases": ["lentils cooked"],
        "kcal": 116,
        "protein_g": 9.0,
        "carb_g": 20.1,
        "fat_g": 0.4,
    },
    {
        "name": "black beans, cooked",
        "aliases": ["black beans cooked"],
        "kcal": 132,
        "protein_g": 8.9,
        "carb_g": 23.7,
        "fat_g": 0.5,
    },
    {
        "name": "potato, boiled",
        "aliases": ["potato boiled", "potato baked"],
        "kcal": 87,
        "protein_g": 1.9,
        "carb_g": 20.1,
        "fat_g": 0.1,
    },
    {
        "name": "olive oil",
        "aliases": ["olive oil", "oil olive"],
        "kcal": 884,
        "protein_g": 0.0,
        "carb_g": 0.0,
        "fat_g": 100.0,
    },
    {
        "name": "shrimp, cooked",
        "aliases": ["shrimp cooked"],
        "kcal": 99,
        "protein_g": 24.0,
        "carb_g": 0.2,
        "fat_g": 0.3,
    },
    {
        "name": "cod, cooked",
        "aliases": ["cod cooked"],
        "kcal": 105,
        "protein_g": 22.8,
        "carb_g": 0.0,
        "fat_g": 0.9,
    },
    {
        "name": "spinach, raw",
        "aliases": ["spinach raw"],
        "kcal": 23,
        "protein_g": 2.9,
        "carb_g": 3.6,
        "fat_g": 0.4,
    },
    {
        "name": "orange, raw",
        "aliases": ["orange raw"],
        "kcal": 47,
        "protein_g": 0.9,
        "carb_g": 11.8,
        "fat_g": 0.1,
    },
    {
        "name": "avocado, raw",
        "aliases": ["avocado raw"],
        "kcal": 160,
        "protein_g": 2.0,
        "carb_g": 8.5,
        "fat_g": 14.7,
    },
    {
        "name": "bread, whole wheat",
        "aliases": ["whole wheat bread", "bread whole wheat"],
        "kcal": 247,
        "protein_g": 13.0,
        "carb_g": 41.0,
        "fat_g": 4.2,
    },
    {
        "name": "cottage cheese",
        "aliases": ["cottage cheese"],
        "kcal": 98,
        "protein_g": 11.1,
        "carb_g": 3.4,
        "fat_g": 4.3,
    },
    {
        "name": "turkey breast",
        "aliases": ["turkey breast"],
        "kcal": 135,
        "protein_g": 30.1,
        "carb_g": 0.0,
        "fat_g": 1.0,
    },
    {
        "name": "edamame",
        "aliases": ["edamame"],
        "kcal": 121,
        "protein_g": 11.9,
        "carb_g": 8.9,
        "fat_g": 5.2,
    },
    {
        "name": "quinoa, cooked",
        "aliases": ["quinoa cooked"],
        "kcal": 120,
        "protein_g": 4.4,
        "carb_g": 21.3,
        "fat_g": 1.9,
    },
]


def _norm(text: str) -> str:
    return text.strip().lower().replace("，", ",")


def search_usda_sr_cache(query: str, fallback_reason: str | None = None) -> NutritionResult | None:
    q = _norm(query)
    best = None
    for row in USDA_SR_CACHE:
        aliases = [row["name"], *row["aliases"]]
        if any(_norm(alias) in q or q in _norm(alias) for alias in aliases):
            best = row
            break
    if best is None:
        return None
    return NutritionResult(
        name=best["name"],
        kcal=float(best["kcal"]),
        protein_g=float(best["protein_g"]),
        carb_g=float(best["carb_g"]),
        fat_g=float(best["fat_g"]),
        serving_size_g=100.0,
        source="usda_fdc",
        source_url="https://fdc.nal.usda.gov/",
        source_detail=(
            "USDA FoodData Central / SR Legacy compact cached reference row; "
            "not generated by an LLM."
        ),
        fetched_at=datetime.now(UTC).isoformat(),
        fallback_used=fallback_reason is not None,
        fallback_from=["usda_fdc_live", "openfoodfacts"] if fallback_reason else [],
        fallback_to="usda_sr_legacy_cache" if fallback_reason else None,
        fallback_reason=fallback_reason,
        raw={"cache": "usda_sr_legacy_compact", "aliases": best["aliases"]},
    )
