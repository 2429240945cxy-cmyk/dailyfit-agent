# Nutrition Source Attribution

Nutrition values must come from tools. Live mode queries Open Food Facts first,
then USDA FoodData Central, then HPB/FOCOS manual cache, then local fallback.

Fallbacks are explicit:

```json
{
  "fallback_used": true,
  "fallback_from": ["openfoodfacts", "usda"],
  "fallback_to": "local_food_db",
  "fallback_reason": "timeout|missing_key|no_match|rate_limited|parse_error"
}
```
