def test_get_current_user_success(client):
    """Happy path: get current user info."""
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(
        "/users/me",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
    assert "created_at" in data


def test_get_current_user_without_auth(client):
    """Auth boundary: cannot access /users/me without token."""
    response = client.get(
        "/users/me"
    )
    
    assert response.status_code == 401

def test_user_isolation_different_users_different_data(client):
    """Auth boundary: each user only sees their own data."""
    # User A
    client.post(
        "/auth/register",
        json={"email": "userX@example.com", "password": "TestPass123"}
    )
    login_a = client.post(
        "/auth/login",
        json={"email": "userX@example.com", "password": "TestPass123"}
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    response_a = client.get(
        "/users/me",
        headers=headers_a
    )
    user_a_data = response_a.json()
    
    # User B
    client.post(
        "/auth/register",
        json={"email": "userY@example.com", "password": "TestPass123"}
    )
    login_b = client.post(
        "/auth/login",
        json={"email": "userY@example.com", "password": "TestPass123"}
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    response_b = client.get(
        "/users/me",
        headers=headers_b
    )
    user_b_data = response_b.json()
    
    # They should be different users
    assert user_a_data["email"] != user_b_data["email"]
    assert user_a_data["id"] != user_b_data["id"]