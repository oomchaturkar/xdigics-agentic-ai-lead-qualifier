from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_scoring_method():
    response = client.get("/api/scoring-method")
    assert response.status_code == 200
    assert response.json()["maximum"] == 100

def test_rejects_empty_companies():
    response = client.post("/api/qualify", json={"companies": ["  "], "research_live": False})
    assert response.status_code == 422
