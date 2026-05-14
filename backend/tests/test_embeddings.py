import pytest

from backend.memory.embeddings import AliyunEmbeddingClient


@pytest.mark.asyncio
async def test_demo_embedding_deterministic(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "demo_mock")
    monkeypatch.setenv("DAILYFIT_DB_PATH", str(tmp_path / "test.db"))
    client = AliyunEmbeddingClient()
    a = await client.embed("牛肉饮食")
    b = await client.embed("牛肉饮食")
    assert a == b
    assert len(a) == 1024
