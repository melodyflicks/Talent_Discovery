from fastapi.testclient import TestClient
from app.main import app
def test_courses_shell(): assert TestClient(app).get("/api/v1/courses").status_code == 200
