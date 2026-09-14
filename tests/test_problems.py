def test_create_problem_success(client):
    """Happy path: create a valid problem."""
    # First, register and login to get auth
    client.post(
        "/auth/register",
        json={"email": "user1@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "user1@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create problem
    response = client.post(
        "/problems",
        json={
            "topic": "arrays",
            "title": "Two Sum",
            "difficulty": "Easy",
            "status": "Completed",
            "date_solved": "2026-08-15"
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "Arrays"  # normalized
    assert data["title"] == "Two Sum"
    assert data["difficulty"] == "Easy"
    assert data["status"] == "Completed"
    assert "id" in data


def test_create_problem_invalid_difficulty(client):
    """Validation: reject invalid difficulty."""
    client.post(
        "/auth/register",
        json={"email": "user2@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "user2@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/problems",
        json={
            "topic": "arrays",
            "title": "Two Sum",
            "difficulty": "InvalidDifficulty",
            "status": "Completed",
            "date_solved": "2026-08-15"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # validation error


def test_create_problem_invalid_status(client):
    """Validation: reject invalid status."""
    client.post(
        "/auth/register",
        json={"email": "user3@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "user3@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/problems",
        json={
            "topic": "arrays",
            "title": "Two Sum",
            "difficulty": "Easy",
            "status": "InvalidStatus",
            "date_solved": "2026-08-15"
        },
        headers=headers
    )
    
    assert response.status_code == 422

def test_user_isolation_cannot_update_other_user_problem(client):
    """Auth boundary: user cannot update another user's problems."""
    # User A creates a problem
    client.post(
        "/auth/register",
        json={"email": "userA@example.com", "password": "TestPass123"}
    )
    login_a = client.post(
        "/auth/login",
        json={"email": "userA@example.com", "password": "TestPass123"}
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    create_response = client.post(
        "/problems",
        json={
            "topic": "arrays",
            "title": "User A Problem",
            "difficulty": "Easy",
            "status": "Completed",
            "date_solved": "2026-08-15"
        },
        headers=headers_a
    )
    problem_id = create_response.json()["id"]
    
    # User B tries to update User A's problem
    client.post(
        "/auth/register",
        json={"email": "userB@example.com", "password": "TestPass123"}
    )
    login_b = client.post(
        "/auth/login",
        json={"email": "userB@example.com", "password": "TestPass123"}
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # User B tries to UPDATE User A's problem — should get 404
    response = client.put(
        f"/problems/{problem_id}",
        json={"status": "Pending"},
        headers=headers_b
    )
    
    assert response.status_code == 404

def test_get_nonexistent_problem(client):
    """Not found: 404 for non-existent problem."""
    client.post(
        "/auth/register",
        json={"email": "user4@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "user4@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to delete a problem that doesn't exist
    response = client.delete(
        "/problems/999999",
        headers=headers
    )
    
    assert response.status_code == 404


def test_create_problem_topic_normalization(client):
    """Edge case: topic whitespace and casing is normalized."""
    client.post(
        "/auth/register",
        json={"email": "user5@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "user5@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create with weird spacing and casing
    response = client.post(
        "/problems",
        json={
            "topic": "  DyNaMiC pRoGrAmMiNg  ",
            "title": "Fibonacci",
            "difficulty": "Medium",
            "status": "Pending",
            "date_solved": "2026-08-15"
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    # Should be normalized to title case with no leading/trailing spaces
    assert data["topic"] == "Dynamic Programming"