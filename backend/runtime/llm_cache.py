from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from backend.runtime.audit_logger import utc_now
from backend.runtime.config import get_settings


def make_cache_key(
    provider: str,
    model: str,
    messages: list[dict[str, str]],
    tools: list[dict] | None,
    temperature: float,
    purpose: str,
) -> str:
    payload = {
        "provider": provider,
        "model": model,
        "messages": messages,
        "tools": tools or [],
        "temperature": temperature,
        "purpose": purpose,
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class LLMCache:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or get_settings().db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure()

    def _ensure(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                create table if not exists llm_cache (
                    cache_key text primary key,
                    provider text not null,
                    model text not null,
                    purpose text not null,
                    response_json text not null,
                    created_at text not null
                )
                """
            )

    def get(self, cache_key: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "select response_json from llm_cache where cache_key = ?", (cache_key,)
            ).fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def set(
        self, cache_key: str, *, provider: str, model: str, purpose: str, response: dict[str, Any]
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                insert or replace into llm_cache(cache_key, provider, model, purpose, response_json, created_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    provider,
                    model,
                    purpose,
                    json.dumps(response, ensure_ascii=False),
                    utc_now(),
                ),
            )
