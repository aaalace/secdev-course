from fastapi.testclient import TestClient

from app.main import _DB, app

client = TestClient(app)


def setup_function():
    global _ID_SEQ
    _DB["issues"].clear()
    _ID_SEQ = 1


def test_validation_title_too_long():
    response = client.post("/issues", json={"title": "x" * 101, "due_at": 1234567890})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "validation_error"


def test_validation_invalid_status():
    response = client.post(
        "/issues",
        json={"title": "Test issue", "status": "invalid_status", "due_at": 1234567890},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "validation_error"


def test_validation_too_many_labels():
    response = client.post(
        "/issues",
        json={
            "title": "Test issue",
            "labels": ["label" + str(i) for i in range(11)],
            "due_at": 1234567890,
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "validation_error"
