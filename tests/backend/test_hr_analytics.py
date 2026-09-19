def test_hr_analytics_dashboard(client, hr_token):
    response = client.get(
        "/api/hr/analytics",
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_employees"] >= 10
    assert data["profile_completion_rate"] > 0
    assert data["total_skills"] >= 15
    assert isinstance(data["skill_distribution"], list)
    assert len(data["skill_distribution"]) > 0
    assert isinstance(data["department_skills"], list)
    assert len(data["department_skills"]) > 0
    assert isinstance(data["skill_gaps"], list)
    assert isinstance(data["role_demand"], list)


def test_hr_sub_analytics_endpoints(client, hr_token):
    # Skills analytics
    res_skills = client.get("/api/hr/skills", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_skills.status_code == 200
    assert isinstance(res_skills.json(), list)

    # Skill gaps analytics
    res_gaps = client.get("/api/hr/skill-gaps", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_gaps.status_code == 200
    assert isinstance(res_gaps.json(), list)

    # Roles bench strength
    res_roles = client.get("/api/hr/roles", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_roles.status_code == 200
    assert isinstance(res_roles.json(), list)

    # Employees list for HR
    res_emps = client.get("/api/hr/employees", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_emps.status_code == 200
    assert len(res_emps.json()) >= 10
