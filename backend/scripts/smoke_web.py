from __future__ import annotations

import json

import httpx


def main() -> None:
    try:
        health = httpx.get("http://127.0.0.1:8000/health", timeout=5).json()
        page = httpx.get("http://127.0.0.1:8000/", timeout=5).text
        ok = health.get("status") == "ok" and "DailyFit Agent" in page
        print(json.dumps({"web_smoke_ok": ok, "health": health}, ensure_ascii=False, indent=2))
        if not ok:
            raise SystemExit(1)
    except Exception as exc:
        print(json.dumps({"web_smoke_ok": False, "error": type(exc).__name__}, ensure_ascii=False))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
