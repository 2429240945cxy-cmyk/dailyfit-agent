from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from backend.runtime.audit_logger import utc_now
from backend.runtime.config import get_settings


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = {
        "qwen-plus": (0.0003, 0.0006),
        "qwen-max": (0.0024, 0.0096),
        "text-embedding-v4": (0.0001, 0.0),
    }
    in_rate, out_rate = rates.get(model, (0.0005, 0.001))
    return round((input_tokens / 1000 * in_rate) + (output_tokens / 1000 * out_rate), 6)


class UsageStore:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or get_settings().db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure()

    def _ensure(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                create table if not exists llm_usage (
                    id text primary key,
                    provider text not null,
                    model text not null,
                    purpose text not null,
                    input_tokens integer not null,
                    output_tokens integer not null,
                    cost_usd real not null,
                    cache_hit integer not null,
                    created_at text not null
                )
                """
            )

    def record(
        self,
        *,
        provider: str,
        model: str,
        purpose: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        cache_hit: bool,
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                insert into llm_usage
                (id, provider, model, purpose, input_tokens, output_tokens, cost_usd, cache_hit, created_at)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid.uuid4().hex,
                    provider,
                    model,
                    purpose,
                    input_tokens,
                    output_tokens,
                    cost_usd,
                    int(cache_hit),
                    utc_now(),
                ),
            )

    def spent_today(self) -> float:
        today = datetime.now(UTC).date().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "select coalesce(sum(cost_usd), 0) from llm_usage where substr(created_at, 1, 10) = ?",
                (today,),
            ).fetchone()
        return float(row[0] or 0.0)

    def today_summary(self) -> dict:
        today = datetime.now(UTC).date().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                select
                  coalesce(sum(input_tokens), 0),
                  coalesce(sum(output_tokens), 0),
                  coalesce(sum(cost_usd), 0),
                  coalesce(avg(cache_hit), 0),
                  count(*)
                from llm_usage
                where substr(created_at, 1, 10) = ?
                """,
                (today,),
            ).fetchone()
        return {
            "date": today,
            "input_tokens": int(row[0] or 0),
            "output_tokens": int(row[1] or 0),
            "cost_usd": float(row[2] or 0.0),
            "cache_hit_rate": float(row[3] or 0.0),
            "call_count": int(row[4] or 0),
        }
