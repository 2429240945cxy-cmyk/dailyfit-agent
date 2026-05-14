import pytest

from backend.runtime.llm import MissingKeyLLM, MockLLM, get_chat_client, get_judge_client


@pytest.mark.asyncio
async def test_mock_llm_deterministic(monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "demo_mock")
    client = get_chat_client()
    assert isinstance(client, MockLLM)
    response = await client.generate([{"role": "user", "content": "hi"}])
    assert response.mode == "demo_mock"
    assert response.provider == "aliyun_openai"


def test_live_missing_key_client(monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "live")
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    client = get_chat_client()
    assert isinstance(client, MissingKeyLLM)


def test_judge_model_must_differ(monkeypatch) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "live")
    monkeypatch.setenv("DAILYFIT_LLM_MODEL", "qwen-plus")
    monkeypatch.setenv("DAILYFIT_JUDGE_MODEL", "qwen-plus")
    client = get_judge_client()
    assert isinstance(client, MissingKeyLLM)
