import pytest
from fastapi.testclient import TestClient

import app.main as main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def clear_db():
    main._DB["issues"].clear()
    main._ID_SEQ = 1
    yield


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_update_issue():
    r1 = client.post("/issues", json={"title": "bug", "labels": [], "due_at": 111})
    assert r1.status_code == 200
    issue = r1.json()
    assert issue["id"] == 1

    r2 = client.put(
        "/issues/1", json={"title": "fixed", "labels": ["done"], "due_at": 222}
    )
    assert r2.status_code == 200
    updated = r2.json()
    assert updated["title"] == "fixed"
    assert updated["labels"] == ["done"]
    assert updated["due_at"] == 222


def test_delete_issue():
    r1 = client.post("/issues", json={"title": "bug", "labels": [], "due_at": 111})
    assert r1.status_code == 200
    assert r1.json()["id"] == 1

    r2 = client.delete("/issues/1")
    assert r2.status_code == 200
    assert r2.json() == {"message": "deleted"}
