# Evaluation Caveats

This project is a portfolio-grade local agent, not a clinical system. Nutrition
datasets are compact. Local dish values vary by recipe and portion size. Guardian
precision/recall is useful for regression checks but not a medical safety
guarantee. E2E judging requires a different Aliyun judge model from the tested
model.

The current live E2E score is intentionally not tuned upward. The judge now
parses valid JSON reliably, so remaining failures mostly reflect real system
gaps: low Open Food Facts/USDA hit rate for Chinese food queries, strict source
attribution expectations, and shallow memory use in some multi-turn cases.
