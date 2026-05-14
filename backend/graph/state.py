from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.guardian.schemas import GuardianVerdict


class UsageInfo(BaseModel):
    provider: str = "aliyun_openai"
    model: str = "qwen-plus"
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    cache_hit: bool = False


class AgentState(BaseModel):
    user_id: str
    session_id: str
    message: str
    intent: str = "general"
    guardian: GuardianVerdict | None = None
    memories: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    response: str = ""
    audit: dict[str, Any] = Field(default_factory=dict)
    mode: str = "demo_mock"
    provider: str = "aliyun_openai"
    model: str = "qwen-plus"
    usage: UsageInfo = Field(default_factory=UsageInfo)
    cost: float = 0.0
    cache_hit: bool = False
    trace_id: str
