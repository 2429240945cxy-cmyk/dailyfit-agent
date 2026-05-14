<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

Always prefix local development commands with `rtk`. If RTK has a dedicated
filter, it uses it. If not, it passes through unchanged.

Examples:

```bash
rtk pytest backend/tests/ -v
rtk python backend/scripts/scan_sensitive_tokens.py
rtk git status
```
<!-- /rtk-instructions -->

# DailyFit Agent Repo Rules

- Never commit real API keys or secrets.
- Keep `.env` ignored; only `.env.example` is committed.
- Live LLM, judge, and embedding calls use Aliyun Bailian / DashScope OpenAI-compatible endpoints.
- Nutrition and exercise ground truth must come from real external datasets or clearly labeled local fallback data.
- Demo and live modes must be explicit in JSON outputs and UI.
