from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path

from backend.memory.schemas import MemoryItem
from backend.runtime.audit_logger import utc_now
from backend.runtime.config import get_settings


class MemoryStore:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else get_settings().db_path
        self._memory_conn: sqlite3.Connection | None = (
            sqlite3.connect(":memory:") if str(self.db_path) == ":memory:" else None
        )
        self._ensure()

    def _connect(self) -> sqlite3.Connection:
        if self._memory_conn is not None:
            return self._memory_conn
        return sqlite3.connect(self.db_path)

    def _ensure(self) -> None:
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        with conn:
            conn.execute(
                """
                create table if not exists memory (
                    id text primary key,
                    user_id text not null,
                    type text not null,
                    summary text not null,
                    retrievable_text text not null,
                    metadata text not null default '{}',
                    created_at text not null,
                    updated_at text not null
                )
                """
            )

    def add(self, item: dict) -> MemoryItem:
        now = utc_now()
        memory = MemoryItem(
            id=item.get("id") or uuid.uuid4().hex,
            user_id=item["user_id"],
            type=item.get("type", "preference"),
            summary=item["summary"],
            retrievable_text=item.get("retrievable_text") or item["summary"],
            metadata=item.get("metadata", {}),
            created_at=item.get("created_at") or now,
            updated_at=item.get("updated_at") or now,
        )
        with self._connect() as conn:
            conn.execute(
                """
                insert or replace into memory
                (id, user_id, type, summary, retrievable_text, metadata, created_at, updated_at)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory.id,
                    memory.user_id,
                    memory.type,
                    memory.summary,
                    memory.retrievable_text,
                    json.dumps(memory.metadata, ensure_ascii=False),
                    memory.created_at,
                    memory.updated_at,
                ),
            )
        return memory

    def list_by_user(self, user_id: str) -> list[MemoryItem]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select id, user_id, type, summary, retrievable_text, metadata, created_at, updated_at
                from memory where user_id = ? order by updated_at desc
                """,
                (user_id,),
            ).fetchall()
        return [
            MemoryItem(
                id=row[0],
                user_id=row[1],
                type=row[2],
                summary=row[3],
                retrievable_text=row[4],
                metadata=json.loads(row[5] or "{}"),
                created_at=row[6],
                updated_at=row[7],
            )
            for row in rows
        ]

    def upsert_profile_memory(self, user_id: str, summary: str, memory_type: str = "profile") -> MemoryItem:
        return self.add(
            {
                "user_id": user_id,
                "type": memory_type,
                "summary": summary,
                "retrievable_text": f"用户{summary}",
                "metadata": {"distilled": True},
            }
        )
