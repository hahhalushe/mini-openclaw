# backend/tests/test_api_sessions.py
from fastapi.testclient import TestClient


def test_create_and_list_sessions():
    from app import app
    with TestClient(app) as client:
        # Create a session
        resp = client.post("/api/sessions", json={"title": "Test Session"})
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        sid = data["id"]

        # List sessions
        resp = client.get("/api/sessions")
        assert resp.status_code == 200
        sessions = resp.json()
        assert any(s["id"] == sid for s in sessions)


def test_session_messages():
    from app import app
    with TestClient(app) as client:
        resp = client.post("/api/sessions", json={"title": "Msg Test"})
        sid = resp.json()["id"]

        # Get messages (should be empty)
        resp = client.get(f"/api/sessions/{sid}/messages")
        assert resp.status_code == 200
        assert resp.json()["messages"] == []


def test_rename_and_delete_session():
    from app import app
    with TestClient(app) as client:
        resp = client.post("/api/sessions", json={"title": "Original"})
        sid = resp.json()["id"]

        # Rename
        resp = client.put(f"/api/sessions/{sid}", json={"title": "Renamed"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Renamed"

        # Delete
        resp = client.delete(f"/api/sessions/{sid}")
        assert resp.status_code == 200


def test_skills_endpoint():
    from app import app
    with TestClient(app) as client:
        resp = client.get("/api/skills")
        assert resp.status_code == 200
        data = resp.json()
        assert "skills" in data


def test_files_read():
    from app import app
    with TestClient(app) as client:
        resp = client.get("/api/files", params={"path": "workspace/SOUL.md"})
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert "soul" in data["content"].lower()


def test_files_blocks_traversal():
    from app import app
    with TestClient(app) as client:
        resp = client.get("/api/files", params={"path": "../../etc/passwd"})
        assert resp.status_code == 403
