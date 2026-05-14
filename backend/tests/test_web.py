from fastapi.testclient import TestClient

from backend.app import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["web"] is True


def test_index_contains_title() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "DailyFit Agent" in response.text


def test_chat_endpoint(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DAILYFIT_MODE", "demo_mock")
    monkeypatch.setenv("DAILYFIT_DB_PATH", str(tmp_path / "web.db"))
    monkeypatch.setenv("DAILYFIT_AUDIT_DIR", str(tmp_path / "audits"))
    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"user_id": "u1", "session_id": "s1", "message": "早餐想吃燕麦"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["trace_id"].startswith("tr_")
    assert payload["source_attribution"]
