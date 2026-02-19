# backend/tests/test_api_config.py
from fastapi.testclient import TestClient


def test_get_engine():
    from app import app
    with TestClient(app) as client:
        resp = client.get("/api/config/engine")
        assert resp.status_code == 200
        assert "engine" in resp.json()


def test_set_engine():
    from app import app
    with TestClient(app) as client:
        resp = client.put("/api/config/engine", json={"engine": "raw_loop"})
        assert resp.status_code == 200
        assert resp.json()["engine"] == "raw_loop"
        # Reset
        client.put("/api/config/engine", json={"engine": "langgraph"})


def test_get_rag_mode():
    from app import app
    with TestClient(app) as client:
        resp = client.get("/api/config/rag-mode")
        assert resp.status_code == 200
        assert "enabled" in resp.json()


def test_token_counting():
    from api.tokens import count_tokens
    tokens = count_tokens("Hello world")
    assert tokens > 0


def test_session_tokens():
    from app import app
    with TestClient(app) as client:
        # Create session first
        resp = client.post("/api/sessions", json={"title": "Token Test"})
        sid = resp.json()["id"]

        resp = client.get(f"/api/tokens/session/{sid}")
        assert resp.status_code == 200
        data = resp.json()
        assert "system_prompt_tokens" in data
        assert "total_tokens" in data


def test_daily_logs():
    from app import app
    with TestClient(app) as client:
        resp = client.get("/api/config/memory/daily-logs")
        assert resp.status_code == 200
        assert "logs" in resp.json()
