from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_security_headers_present():
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"


def test_security_headers_on_all_endpoints():
    response = client.get("/issues")
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
