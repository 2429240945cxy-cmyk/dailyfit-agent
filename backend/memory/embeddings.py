from __future__ import annotations

import json
import os
import sqlite3
import uuid
from pathlib import Path

from backend.runtime.audit_logger import utc_now
from backend.runtime.config import get_settings
from backend.runtime.demo_mode import deterministic_embedding
from backend.runtime.llm_cache import LLMCache, make_cache_key
from backend.runtime.llm_usage import UsageStore, estimate_cost_usd


class AliyunEmbeddingClient:
    def __init__(self, db_path: Path | None = None) -> None:
        self.settings = get_settings()
        self.db_path = db_path or self.settings.db_path
        self.cache = LLMCache(self.db_path)
        self.usage_store = UsageStore(self.db_path)
        self._ensure()

    def _ensure(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
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
                """
            )

    async def embed(self, text: str, purpose: str = "memory_embedding") -> list[float]:
        if self.settings.mode == "demo_mock" or not os.getenv("DASHSCOPE_API_KEY"):
            vector = deterministic_embedding(text, self.settings.embedding_dim)
            self.usage_store.record(
                provider=self.settings.embedding_provider,
                model=self.settings.embedding_model,
                purpose=purpose,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                cache_hit=False,
            )
            return vector

        cache_key = make_cache_key(
            self.settings.embedding_provider,
            self.settings.embedding_model,
            [{"role": "user", "content": text}],
            None,
            0.0,
            purpose,
        )
        cached = self.cache.get(cache_key)
        if cached:
            self.usage_store.record(
                provider=self.settings.embedding_provider,
                model=self.settings.embedding_model,
                purpose=purpose,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                cache_hit=True,
            )
            return cached["vector"]

        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"), base_url=self.settings.dashscope_base_url
        )
        response = await client.embeddings.create(model=self.settings.embedding_model, input=text)
        vector = list(response.data[0].embedding)
        input_tokens = int(getattr(getattr(response, "usage", None), "prompt_tokens", 0) or len(text) // 4)
        cost = estimate_cost_usd(self.settings.embedding_model, input_tokens, 0)
        self.cache.set(
            cache_key,
            provider=self.settings.embedding_provider,
            model=self.settings.embedding_model,
            purpose=purpose,
            response={"vector": vector},
        )
        self.usage_store.record(
            provider=self.settings.embedding_provider,
            model=self.settings.embedding_model,
            purpose=purpose,
            input_tokens=input_tokens,
            output_tokens=0,
            cost_usd=cost,
            cache_hit=False,
        )
        return vector

    def store_embedding(self, memory_id: str, vector: list[float]) -> str:
        embedding_id = uuid.uuid4().hex
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                insert into embeddings(id, memory_id, provider, model, dim, vector_json, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    embedding_id,
                    memory_id,
                    self.settings.embedding_provider,
                    self.settings.embedding_model,
                    len(vector),
                    json.dumps(vector),
                    utc_now(),
                ),
            )
        return embedding_id
