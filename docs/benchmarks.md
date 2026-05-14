# Benchmarks

Run all demo benchmarks:

```bash
DAILYFIT_MODE=demo_mock python backend/scripts/run_all_v2_benchmarks.py
python backend/scripts/save_baseline.py
python backend/scripts/verify_readme_numbers.py
```

Live benchmarks require `DASHSCOPE_API_KEY` and optional `USDA_API_KEY`.
