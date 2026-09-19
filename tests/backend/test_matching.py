from fastapi.testclient import TestClient
from app.main import app
def test_matching_shell(): assert TestClient(app).get("/api/v1/matching/status").status_code == 200
