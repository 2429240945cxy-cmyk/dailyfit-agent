# Evaluation Caveats

This project is a portfolio-grade local agent, not a clinical system. Nutrition
datasets are compact. Local dish values vary by recipe and portion size. Guardian
precision/recall is useful for regression checks but not a medical safety
guarantee. E2E judging requires a different Aliyun judge model from the tested
model.

v6 kept the E2E dataset, judge threshold, and rubric unchanged. The pass-rate
increase comes from system changes: Chinese food lookup normalization, a
clearly labeled USDA SR Legacy cache, live LLM answer synthesis, broader memory
patterns, and Guardian-to-workout injury filtering.

E2E judge scores can vary by roughly 0.05 across live runs because the tested
agent and judge are remote LLM calls. The accepted v6 run is 0.6333 with
judge_parse_success_rate 1.0 and no heuristic fallback. Runs above 0.70 should
be treated as suspicious and reviewed for source/cache overfitting before being
reported.
