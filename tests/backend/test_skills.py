from fastapi.testclient import TestClient
from app.main import app
def test_skills_shell(): assert TestClient(app).get("/api/v1/skills").json() == []
