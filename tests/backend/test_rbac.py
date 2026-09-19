def test_hr_analytics_access_by_admin(client, admin_token):
    response = client.get(
        "/api/hr/analytics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "total_employees" in response.json()


def test_hr_analytics_access_by_hr(client, hr_token):
    response = client.get(
        "/api/hr/analytics",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert response.status_code == 200


def test_hr_analytics_forbidden_for_employee(client, employee_token_and_profile):
    emp_token, _, _ = employee_token_and_profile
    response = client.get(
        "/api/hr/analytics",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]


def test_employee_cannot_access_other_employee_data(
    client, employee_token_and_profile, second_employee_token_and_profile
):
    emp_token1, profile1, _ = employee_token_and_profile
    _, profile2, _ = second_employee_token_and_profile

    # Employee 1 tries to access Employee 2 profile
    response = client.get(
        f"/api/employees/{profile2.id}",
        headers={"Authorization": f"Bearer {emp_token1}"}
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

    # Employee 1 tries to access Employee 2 skills
    response = client.get(
        f"/api/employees/{profile2.id}/skills",
        headers={"Authorization": f"Bearer {emp_token1}"}
    )
    assert response.status_code == 403

    # Employee 1 tries to access Employee 2 matches
    response = client.get(
        f"/api/employees/{profile2.id}/matches",
        headers={"Authorization": f"Bearer {emp_token1}"}
    )
    assert response.status_code == 403


def test_hr_can_access_any_employee_data(client, hr_token, employee_token_and_profile):
    _, profile1, _ = employee_token_and_profile
    response = client.get(
        f"/api/employees/{profile1.id}",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == profile1.id
