from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import IssueModel

client = TestClient(app)


def setup_function():
    db = SessionLocal()
    db.query(IssueModel).delete()
    db.commit()

    db.add(IssueModel(title="Test issue", labels=[], due_at=1234567890, status="open"))
    db.add(
        IssueModel(title="Another task", labels=[], due_at=1234567890, status="open")
    )
    db.commit()
    db.close()


def test_search_safe_from_sql_injection():
    malicious_input = "' OR '1'='1"
    response = client.get(f"/issues?search={malicious_input}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_search_finds_legitimate_results():
    response = client.get("/issues?search=Test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "Test issue" in data[0]["title"]
