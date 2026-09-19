def test_list_courses(client, employee_token_and_profile):
    token, _, _ = employee_token_and_profile
    response = client.get(
        "/api/courses",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) >= 5


def test_get_employee_recommendations(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    response = client.get(
        f"/api/employees/{profile.id}/recommendations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    recs = response.json()
    assert isinstance(recs, list)
    assert len(recs) >= 1
    assert "course" in recs[0]


def test_get_employee_roadmap(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    response = client.get(
        f"/api/employees/{profile.id}/roadmap",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "roadmap_data" in data
    assert "phases" in data["roadmap_data"]
