# API tests: the LLM and vector search are replaced with fakes so the tests run anywhere.
import pytest
from fastapi.testclient import TestClient

from backend.app import config, database, crypto, pipeline, main


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(main, "build_index", lambda: 0)
    monkeypatch.setattr(main, "get_collection", lambda: type("C", (), {"count": lambda self: 1})())
    fake = [{"sid": "S1", "text": "Adults need 7 to 9 hours of sleep.", "org": "CSEP", "title": "24h",
             "url": "https://csepguidelines.ca", "doc_id": "physical_activity_csep"}]
    monkeypatch.setattr(pipeline, "retrieve", lambda q: fake if "sleep" in q.lower() else [])
    monkeypatch.setattr(pipeline, "ask_model", lambda s, u, m=None: "Adults need 7 to 9 hours of sleep [S1].")
    with TestClient(main.app) as c:
        yield c


def test_consent_gate(client):
    assert client.post("/api/ask", json={"text": "How much sleep?"}).status_code == 403
    assert client.get("/api/profile").status_code == 403


def test_full_flow(client):
    client.post("/api/consent")
    r = client.put("/api/profile", json={"age": 30, "sleep_hours": 5.5})
    assert r.json()["comparison"][0]["status"] == "below"
    a = client.post("/api/ask", json={"text": "How much sleep do adults need?"}).json()
    assert a["outcome"] == "answered" and a["sources"][0]["url"].startswith("https://")
    assert "[S1]" not in a["answer"]
    assert len(client.get("/api/history").json()) == 1
    assert client.post("/api/feedback", json={"history_id": a["history_id"], "rating": 5}).status_code == 200


def test_redirect_and_decline(client):
    client.post("/api/consent")
    assert client.post("/api/ask", json={"text": "Do I have insomnia?"}).json()["outcome"] == "redirected"
    assert client.post("/api/ask", json={"text": "Best cryptocurrency to buy?"}).json()["outcome"] == "declined"


def test_profile_validation(client):
    client.post("/api/consent")
    assert client.put("/api/profile", json={"sleep_hours": 99}).status_code == 422


def test_data_is_encrypted_and_deletable(client):
    client.post("/api/consent")
    client.put("/api/profile", json={"age": 41, "sleep_hours": 6.25})
    conn = database.get_conn()
    raw = conn.execute("SELECT data_enc FROM profile").fetchone()["data_enc"]
    conn.close()
    assert "6.25" not in raw and "sleep" not in raw
    client.delete("/api/my-data")
    assert client.get("/api/consent").json()["accepted"] is False
    conn = database.get_conn()
    assert conn.execute("SELECT COUNT(*) FROM profile").fetchone()[0] == 0
    conn.close()
