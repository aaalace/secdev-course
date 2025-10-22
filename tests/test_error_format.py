from fastapi.testclient import TestClient

from app.main import _DB, app

client = TestClient(app)


def setup_function():
    global _ID_SEQ
    _DB["issues"].clear()
    _ID_SEQ = 1


def test_error_format_not_found():
    response = client.get("/issues/52")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == "nf_error"
    assert data["error"]["message"] == "Issue not found"


def test_error_format_invalid_id():
    response = client.get("/issues/-52")
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "invalid_id"
    assert data["error"]["message"] == "Issue ID must be positive"


def test_error_format_validation():
    response = client.post("/issues", json={"title": "", "due_at": 123454321})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "validation_error"
