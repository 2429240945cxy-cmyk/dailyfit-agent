# Self-Audit

`backend/scripts/run_self_audit.py` runs tests, benchmarks, secret scan, and
README verification. Regressions can create GitHub issues when `gh` is
available.

Auto-fix must not modify `.env`, secrets, benchmark datasets, guardian labels,
dataset construction docs, or CI secret configuration.
