def test_list_roles(client, employee_token_and_profile):
    token, _, _ = employee_token_and_profile
    response = client.get(
        "/api/roles",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) >= 5
    assert "required_skills" in roles[0]


def test_get_employee_matches(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    response = client.get(
        f"/api/employees/{profile.id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) >= 1
    assert "match_score" in matches[0]
    assert "matching_skills" in matches[0]


def test_generate_employee_matches(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    response = client.post(
        f"/api/employees/{profile.id}/matches/generate",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) >= 1


def test_get_employee_skill_gaps(client, employee_token_and_profile):
    token, profile, _ = employee_token_and_profile
    response = client.get(
        f"/api/employees/{profile.id}/skill-gaps",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    gaps = response.json()
    assert isinstance(gaps, list)
