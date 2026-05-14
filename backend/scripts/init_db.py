from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.runtime.config import get_settings

DDL = [
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
    """,
    """
    create table if not exists embeddings (
        id text primary key,
        memory_id text,
        provider text not null,
        model text not null,
        dim integer not null,
        vector_json text not null,
        created_at text not null
    )
    """,
    """
    create table if not exists audit (
        trace_id text primary key,
        created_at text,
        mode text,
        user_id text,
        session_id text,
        payload text not null
    )
    """,
    """
    create table if not exists profiles (
        user_id text primary key,
        profile_json text not null,
        updated_at text not null
    )
    """,
    """
    create table if not exists meal_logs (
        id text primary key,
        user_id text not null,
        session_id text,
        meal_json text not null,
        created_at text not null
    )
    """,
    """
    create table if not exists workout_logs (
        id text primary key,
        user_id text not null,
        session_id text,
        workout_json text not null,
        created_at text not null
    )
    """,
    """
    create table if not exists llm_cache (
        cache_key text primary key,
        provider text not null,
        model text not null,
        purpose text not null,
        response_json text not null,
        created_at text not null
    )
    """,
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
    """,
    """
    create table if not exists benchmark_runs (
        id text primary key,
        benchmark text not null,
        dataset text not null,
        mode text not null,
        result_json text not null,
        created_at text not null
    )
    """,
]


def init_db(path: str | Path | None = None) -> Path:
    settings = get_settings()
    db_path = Path(path) if path is not None else settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        for ddl in DDL:
            conn.execute(ddl)
    settings.audit_dir.mkdir(parents=True, exist_ok=True)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    return db_path


def main() -> None:
    db_path = init_db()
    print(f"initialized {db_path}")


if __name__ == "__main__":
    main()
