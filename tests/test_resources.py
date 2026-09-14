def test_create_resource_success(client):
    """Happy path: create a valid resource."""
    client.post(
        "/auth/register",
        json={"email": "res1@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "res1@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/resources",
        json={
            "topic": "arrays",
            "title": "LeetCode Arrays Guide",
            "url": "https://leetcode.com/explore/arrays",
            "notes": "Great for beginners"
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "arrays"
    assert data["title"] == "LeetCode Arrays Guide"
    assert data["url"] == "https://leetcode.com/explore/arrays"
    assert "id" in data
    assert "created_at" in data


def test_create_resource_missing_fields(client):
    """Validation: reject missing required fields."""
    client.post(
        "/auth/register",
        json={"email": "res2@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "res2@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Missing URL
    response = client.post(
        "/resources",
        json={
            "topic": "arrays",
            "title": "Some Guide",
            "url": "",
            "notes": "test"
        },
        headers=headers
    )
    
    assert response.status_code == 422


def test_user_isolation_cannot_delete_other_user_resource(client):
    """Auth boundary: user cannot delete another user's resources."""
    # User A creates a resource
    client.post(
        "/auth/register",
        json={"email": "resA@example.com", "password": "TestPass123"}
    )
    login_a = client.post(
        "/auth/login",
        json={"email": "resA@example.com", "password": "TestPass123"}
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    create_response = client.post(
        "/resources",
        json={
            "topic": "strings",
            "title": "User A Resource",
            "url": "https://example.com",
            "notes": "test"
        },
        headers=headers_a
    )
    resource_id = create_response.json()["id"]
    
    # User B tries to delete User A's resource
    client.post(
        "/auth/register",
        json={"email": "resB@example.com", "password": "TestPass123"}
    )
    login_b = client.post(
        "/auth/login",
        json={"email": "resB@example.com", "password": "TestPass123"}
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    response = client.delete(
        f"/resources/{resource_id}",
        headers=headers_b
    )
    
    assert response.status_code == 404


def test_delete_nonexistent_resource(client):
    """Not found: 404 for non-existent resource."""
    client.post(
        "/auth/register",
        json={"email": "res3@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "res3@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(
        "/resources/999999",
        headers=headers
    )
    
    assert response.status_code == 404


def test_get_resources_empty(client):
    """Happy path: get resources when none exist."""
    client.post(
        "/auth/register",
        json={"email": "res4@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "res4@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(
        "/resources",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json() == []