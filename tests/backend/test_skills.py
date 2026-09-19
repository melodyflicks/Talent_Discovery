def test_list_skills(client, employee_token_and_profile):
    token, _, _ = employee_token_and_profile
    response = client.get(
        "/api/skills",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) >= 15
    skill_names = [s["name"] for s in skills]
    assert "Python" in skill_names
    assert "FastAPI" in skill_names


def test_add_employee_skill_with_evidence(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    payload = {
        "skill_name": "Docker",
        "proficiency": 4,
        "confidence": 0.90,
        "skill_type": "explicit",
        "source": "peer-review",
        "evidence_text": "Successfully containerized payment service in production."
    }
    response = client.post(
        f"/api/employees/{profile.id}/skills",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["proficiency"] == 4
    assert len(data["evidence"]) >= 1


def test_get_employee_skills(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    response = client.get(
        f"/api/employees/{profile.id}/skills",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) >= 1
