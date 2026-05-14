from __future__ import annotations

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    id: str | None = None
    user_id: str
    type: str
    summary: str
    retrievable_text: str
    metadata: dict = Field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None


class MemoryHit(BaseModel):
    id: str | None = None
    summary: str
    retrievable_text: str
    score: float
    source: str = "hybrid"
    metadata: dict = Field(default_factory=dict)
