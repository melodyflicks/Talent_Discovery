from app.core.config import settings


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert data["database"] in ("connected", "unavailable")


def test_login_success_admin(client):
    admin_pw = settings.default_admin_password or "CHANGE_ADMIN_PASSWORD"
    response = client.post(
        "/api/auth/login",
        json={"email": "admin1@talent.local", "password": admin_pw}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin1@talent.local"
    assert data["user"]["role"] == "admin"


def test_login_success_hr(client):
    hr_pw = settings.default_hr_password or "CHANGE_HR_PASSWORD"
    response = client.post(
        "/api/auth/login",
        json={"email": "hr1@talent.local", "password": hr_pw}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "hr"


def test_login_invalid_password(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin1@talent.local", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@talent.local", "password": "AnyPassword!"}
    )
    assert response.status_code == 401


def test_auth_me_endpoint(client, admin_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin1@talent.local"
    assert data["role"] == "admin"
    assert "password_hash" not in data


def test_auth_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
