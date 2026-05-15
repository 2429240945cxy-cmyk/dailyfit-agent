# Dev Tools

Common commands:

```bash
rtk python backend/scripts/init_db.py
rtk pytest backend/tests/ -v
rtk python backend/scripts/scan_sensitive_tokens.py
rtk uvicorn backend.app:app --port 8000
```

Live smoke and E2E judge debugging:

```bash
rtk powershell -NoProfile -Command "$env:DAILYFIT_MODE='live'; rtk python backend/scripts/smoke_llm.py"
rtk powershell -NoProfile -Command "$env:DAILYFIT_MODE='live'; rtk python backend/scripts/run_e2e_benchmark.py"
```

Set `DAILYFIT_E2E_LIMIT` and `DAILYFIT_E2E_OFFSET` for quick targeted live judge
checks without overwriting the canonical `e2e_v2.json` result.
