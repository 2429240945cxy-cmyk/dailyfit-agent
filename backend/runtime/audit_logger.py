from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.runtime.config import get_settings


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def new_trace_id() -> str:
    return f"tr_{uuid.uuid4().hex[:16]}"


def default_audit_record(
    *,
    trace_id: str,
    user_id: str,
    session_id: str,
    mode: str,
    provider: str,
    model: str,
    message: str = "",
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "mode": mode,
        "user_id": user_id,
        "session_id": session_id,
        "provider": provider,
        "model": model,
        "message": message,
        "guardian": {},
        "intent": "general",
        "memory_hits": [],
        "tool_calls": [],
        "tool_results": [],
        "nutrition_source_fallback": None,
        "llm_usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "cache_hit": False,
        },
        "final_response": "",
        "created_at": utc_now(),
    }


class AuditLogger:
    def __init__(self, audit_dir: Path | None = None, db_path: Path | None = None) -> None:
        settings = get_settings()
        self.audit_dir = audit_dir or settings.audit_dir
        self.db_path = db_path or settings.db_path
        self.audit_dir.mkdir(parents=True, exist_ok=True)

    def write(self, record: dict[str, Any]) -> Path:
        trace_id = str(record.get("trace_id") or new_trace_id())
        record["trace_id"] = trace_id
        record.setdefault("created_at", utc_now())
        path = self.audit_dir / f"{trace_id}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        self._write_sqlite(record)
        return path

    def _write_sqlite(self, record: dict[str, Any]) -> None:
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    create table if not exists audit (
                        trace_id text primary key,
                        created_at text,
                        mode text,
                        user_id text,
                        session_id text,
                        payload text not null
                    )
                    """
                )
                conn.execute(
                    """
                    insert or replace into audit(trace_id, created_at, mode, user_id, session_id, payload)
                    values (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("trace_id"),
                        record.get("created_at"),
                        record.get("mode"),
                        record.get("user_id"),
                        record.get("session_id"),
                        json.dumps(record, ensure_ascii=False),
                    ),
                )
        except sqlite3.Error:
            # JSON audit is the primary audit artifact; SQLite write failures must not hide it.
            return

    def read(self, trace_id: str) -> dict[str, Any] | None:
        path = self.audit_dir / f"{trace_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        files = sorted(self.audit_dir.glob("tr_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        rows = []
        for path in files[:limit]:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            rows.append(
                {
                    "trace_id": payload.get("trace_id"),
                    "created_at": payload.get("created_at"),
                    "mode": payload.get("mode"),
                    "intent": payload.get("intent"),
                    "final_response": payload.get("final_response", "")[:160],
                }
            )
        return rows
