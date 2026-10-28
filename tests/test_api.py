"""
End-to-End API Integration Tests for Echoes.exe Flask Endpoints
"""
import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"ECHOES.EXE" in resp.data
    assert b"GHOST TERMINAL" in resp.data


def test_api_config(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["app_name"] == "Echoes.exe"
    assert "ai_provider" in data
    assert "storage" in data


def test_api_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"


def test_api_devrelay_status(client):
    resp = client.get("/api/devrelay/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["gateway_connected"] is True
    assert data["dev_author"] == "priyank_dev"


def test_analyze_sample_and_interview(client):
    # 1. Analyze sample repo
    resp = client.post("/api/analyze/sample", json={"sample_id": "canvas-nest-legacy"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["evidence"]["project_name"] == "canvas-nest-legacy"
    session_id = data["session_id"]

    # 2. Interview Ghost
    resp_chat = client.post("/api/interview", json={
        "session_id": session_id,
        "question": "What was your purpose and who wrote your first commit?"
    })
    assert resp_chat.status_code == 200
    chat_data = resp_chat.get_json()
    assert chat_data["success"] is True
    assert "answer" in chat_data
    assert len(chat_data["supporting_evidence"]) > 0

    # 3. Save to Vault
    resp_save = client.post("/api/investigations/save", json={
        "session_id": session_id,
        "cloud_consent": False,
        "mode": "local"
    })
    assert resp_save.status_code == 200
    save_data = resp_save.get_json()
    assert save_data["success"] is True

    # 4. List Vault
    resp_list = client.get("/api/investigations")
    assert resp_list.status_code == 200
    list_data = resp_list.get_json()
    assert len(list_data["investigations"]) >= 1

    # 5. Export Markdown & JSON
    resp_md = client.post("/api/export/markdown", json={"report": data["report"]})
    assert resp_md.status_code == 200
    assert b"Echoes.exe" in resp_md.data

    resp_json = client.post("/api/export/json", json={"report": data["report"]})
    assert resp_json.status_code == 200
    exported = json.loads(resp_json.data)
    assert exported["project_name"] == "canvas-nest-legacy"
