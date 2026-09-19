def test_list_employees(client, hr_token):
    response = client.get(
        "/api/employees",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10


def test_get_my_profile(client, employee_token_and_profile):
    token, profile, user = employee_token_and_profile
    response = client.get(
        "/api/profiles/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == profile.id
    assert data["user_id"] == user.id
    assert "skills" in data


def test_update_my_profile(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    response = client.put(
        "/api/profiles/me",
        json={"bio": "Updated bio via test suite", "location": "Remote, US"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "Updated bio via test suite"
    assert data["location"] == "Remote, US"


def test_admin_create_employee(client, admin_token):
    payload = {
        "email": "new.hire@talent.local",
        "password": "Password123!",
        "full_name": "New Hire",
        "employee_code": "EMP999",
        "department": "Engineering",
        "designation": "Junior Backend Developer",
        "years_of_experience": 1.0,
        "education": "B.S. in Computer Science",
        "location": "San Francisco, CA",
        "bio": "Excited new team member."
    }
    response = client.post(
        "/api/employees",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["employee_code"] == "EMP999"
    assert data["designation"] == "Junior Backend Developer"
