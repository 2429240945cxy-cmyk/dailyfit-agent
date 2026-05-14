from backend.runtime.budget import BudgetManager
from backend.runtime.llm_cache import LLMCache, make_cache_key
from backend.runtime.llm_usage import UsageStore


def test_cache_roundtrip(tmp_path) -> None:
    cache = LLMCache(tmp_path / "cache.db")
    key = make_cache_key("aliyun_openai", "qwen-plus", [{"role": "user", "content": "hi"}], None, 0, "chat")
    cache.set(key, provider="aliyun_openai", model="qwen-plus", purpose="chat", response={"content": "ok"})
    assert cache.get(key)["content"] == "ok"


def test_usage_and_budget(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_DB_PATH", str(tmp_path / "usage.db"))
    monkeypatch.setenv("DAILYFIT_BUDGET_USD", "0.001")
    store = UsageStore()
    store.record(
        provider="aliyun_openai",
        model="qwen-plus",
        purpose="chat",
        input_tokens=10,
        output_tokens=10,
        cost_usd=0.002,
        cache_hit=False,
    )
    status = BudgetManager(store).check()
    assert status.budget_exceeded is True
