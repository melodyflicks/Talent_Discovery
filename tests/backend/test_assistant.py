def test_assistant_chat(client, employee_token_and_profile):
    token, _, _ = employee_token_and_profile
    response = client.post(
        "/api/assistant/chat",
        json={"message": "What skills do I need for senior roles?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "suggestions" in data
    assert len(data["reply"]) > 10
