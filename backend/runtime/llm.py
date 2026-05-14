from __future__ import annotations

import json
import os
from typing import Protocol

from pydantic import BaseModel, Field

from backend.runtime.budget import BudgetManager
from backend.runtime.config import get_settings
from backend.runtime.demo_mode import load_mock_responses
from backend.runtime.llm_cache import LLMCache, make_cache_key
from backend.runtime.llm_usage import UsageStore, estimate_cost_usd


class LLMResponse(BaseModel):
    content: str
    tool_calls: list[dict] = Field(default_factory=list)
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    cache_hit: bool = False
    mode: str
    raw: dict | None = None
    error: str | None = None


class LLMClient(Protocol):
    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        purpose: str = "chat",
    ) -> LLMResponse:
        ...


def _estimate_tokens(messages: list[dict[str, str]]) -> int:
    return max(1, sum(len(m.get("content", "")) for m in messages) // 4)


class MockLLM:
    def __init__(self, model: str = "mock-qwen-plus") -> None:
        self.responses = load_mock_responses()
        self.provider = "aliyun_openai"
        self.model = model

    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        purpose: str = "chat",
    ) -> LLMResponse:
        content = self.responses.get(purpose) or self.responses.get("chat", "")
        if purpose == "judge":
            content = self.responses.get("judge", "{}")
        return LLMResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            cache_hit=False,
            mode="demo_mock",
            raw={"mock": True, "tools": bool(tools), "temperature": temperature},
        )


class MissingKeyLLM:
    def __init__(self, provider: str = "aliyun_openai", reason: str = "DASHSCOPE_API_KEY missing"):
        self.provider = provider
        self.reason = reason
        self.model = get_settings().llm_model

    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        purpose: str = "chat",
    ) -> LLMResponse:
        return LLMResponse(
            content="Live mode was requested, but DASHSCOPE_API_KEY is missing. No live model call was made.",
            provider=self.provider,
            model=self.model,
            mode="live_missing_key_not_run",
            error=self.reason,
            raw={"fallback_used": False, "missing_key": True, "purpose": purpose},
        )


class BudgetExceededLLM(MockLLM):
    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        purpose: str = "chat",
    ) -> LLMResponse:
        response = await super().generate(messages, tools, temperature, purpose)
        status = BudgetManager().check()
        response.mode = "live_with_fallback"
        response.error = "budget_exceeded"
        response.raw = {
            "fallback_used": True,
            "fallback_from": ["aliyun_openai"],
            "fallback_to": "mock_llm",
            "fallback_reason": "budget_exceeded",
            **status.model_dump(),
        }
        return response


class AliyunOpenAIClient:
    def __init__(
        self,
        model: str,
        base_url: str,
        provider: str = "aliyun_openai",
        cache: LLMCache | None = None,
        usage_store: UsageStore | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.cache = cache or LLMCache()
        self.usage_store = usage_store or UsageStore()

    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict] | None = None,
        temperature: float = 0.0,
        purpose: str = "chat",
    ) -> LLMResponse:
        budget_status = BudgetManager(self.usage_store).check()
        if budget_status.budget_exceeded:
            return await BudgetExceededLLM(model=f"budget-fallback-{self.model}").generate(
                messages, tools, temperature, purpose
            )

        cache_key = make_cache_key(
            self.provider, self.model, messages, tools, temperature, purpose
        )
        cached = self.cache.get(cache_key)
        if cached:
            response = LLMResponse(**cached)
            response.cache_hit = True
            self.usage_store.record(
                provider=self.provider,
                model=self.model,
                purpose=purpose,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                cache_hit=True,
            )
            return response

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"), base_url=self.base_url)
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools
            completion = await client.chat.completions.create(**kwargs)
            choice = completion.choices[0]
            content = choice.message.content or ""
            raw_usage = getattr(completion, "usage", None)
            input_tokens = int(getattr(raw_usage, "prompt_tokens", 0) or _estimate_tokens(messages))
            output_tokens = int(getattr(raw_usage, "completion_tokens", 0) or max(1, len(content) // 4))
            cost = estimate_cost_usd(self.model, input_tokens, output_tokens)
            tool_calls = []
            if getattr(choice.message, "tool_calls", None):
                tool_calls = [json.loads(tc.model_dump_json()) for tc in choice.message.tool_calls]
            response = LLMResponse(
                content=content,
                tool_calls=tool_calls,
                provider=self.provider,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                cache_hit=False,
                mode="live_real",
                raw={"id": completion.id, "created": completion.created},
            )
            self.cache.set(
                cache_key,
                provider=self.provider,
                model=self.model,
                purpose=purpose,
                response=response.model_dump(),
            )
            self.usage_store.record(
                provider=self.provider,
                model=self.model,
                purpose=purpose,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                cache_hit=False,
            )
            return response
        except Exception as exc:
            return LLMResponse(
                content="Live model call failed. The failure was recorded in the audit trace.",
                provider=self.provider,
                model=self.model,
                input_tokens=_estimate_tokens(messages),
                output_tokens=0,
                cost_usd=0.0,
                cache_hit=False,
                mode="live_with_fallback",
                error=type(exc).__name__,
                raw={
                    "fallback_used": True,
                    "fallback_from": ["aliyun_openai"],
                    "fallback_to": "mock_llm",
                    "fallback_reason": "timeout|missing_key|no_match|rate_limited|parse_error",
                    "error_type": type(exc).__name__,
                },
            )


def get_chat_client() -> LLMClient:
    settings = get_settings()
    if settings.mode == "demo_mock":
        return MockLLM(model="mock-qwen-plus")
    if settings.mode == "live":
        if not os.getenv("DASHSCOPE_API_KEY"):
            return MissingKeyLLM(provider="aliyun_openai", reason="DASHSCOPE_API_KEY missing")
        return AliyunOpenAIClient(model=settings.llm_model, base_url=settings.dashscope_base_url)
    return MockLLM(model="mock-qwen-plus")


def get_judge_client() -> LLMClient:
    settings = get_settings()
    if settings.mode == "demo_mock":
        return MockLLM(model="mock-qwen-max")
    if settings.judge_model == settings.llm_model:
        return MissingKeyLLM(provider="aliyun_openai", reason="judge model must differ")
    if not os.getenv("DASHSCOPE_API_KEY"):
        return MissingKeyLLM(provider="aliyun_openai", reason="DASHSCOPE_API_KEY missing")
    return AliyunOpenAIClient(model=settings.judge_model, base_url=settings.dashscope_base_url)
