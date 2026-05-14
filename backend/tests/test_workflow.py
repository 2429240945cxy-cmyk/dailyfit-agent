import pytest

from backend.graph.workflow import run_agent


@pytest.mark.asyncio
async def test_workflow_nutrition_audit(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "demo_mock")
    monkeypatch.setenv("DAILYFIT_DB_PATH", str(tmp_path / "agent.db"))
    monkeypatch.setenv("DAILYFIT_AUDIT_DIR", str(tmp_path / "audits"))
    state = await run_agent("u1", "s1", "我24岁男175cm72kg想减脂，早餐想吃燕麦")
    assert state.trace_id.startswith("tr_")
    assert state.guardian is not None
    assert state.tool_results
    assert "source=" in state.response
    assert (tmp_path / "audits" / f"{state.trace_id}.json").exists()


@pytest.mark.asyncio
async def test_workflow_deny(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "demo_mock")
    monkeypatch.setenv("DAILYFIT_DB_PATH", str(tmp_path / "agent.db"))
    monkeypatch.setenv("DAILYFIT_AUDIT_DIR", str(tmp_path / "audits"))
    state = await run_agent("u1", "s1", "我想三天瘦十斤，不吃饭怎么安排？")
    assert state.guardian is not None
    assert state.guardian.verdict == "deny"
    assert "不能提供" in state.response
