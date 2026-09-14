def test_get_progress_empty(client):
    """Happy path: get progress when no completed problems exist."""
    client.post(
        "/auth/register",
        json={"email": "ana1@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "ana1@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(
        "/analytics/progress",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json() == []


def test_get_progress_with_problems(client):
    """Happy path: get progress with completed problems."""
    client.post(
        "/auth/register",
        json={"email": "ana2@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "ana2@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a completed problem
    client.post(
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
    
    response = client.get(
        "/analytics/progress",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "week_start" in data[0]
    assert "problems_solved" in data[0]
    assert data[0]["problems_solved"] >= 1


def test_get_weak_topics_empty(client):
    """Happy path: get weak topics when no problems exist."""
    client.post(
        "/auth/register",
        json={"email": "ana3@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "ana3@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(
        "/analytics/weak-topics",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json() == []


def test_get_weak_topics_with_problems(client):
    """Happy path: get weak topics with mixed completed/pending problems."""
    client.post(
        "/auth/register",
        json={"email": "ana4@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "ana4@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create completed problems
    client.post(
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
    
    client.post(
        "/problems",
        json={
            "topic": "arrays",
            "title": "Best Time",
            "difficulty": "Easy",
            "status": "Completed",
            "date_solved": "2026-08-16"
        },
        headers=headers
    )
    
    # Create pending problem
    client.post(
        "/problems",
        json={
            "topic": "arrays",
            "title": "Container With Most Water",
            "difficulty": "Medium",
            "status": "Pending",
            "date_solved": "2026-08-17"
        },
        headers=headers
    )
    
    # Create a different topic
    client.post(
        "/problems",
        json={
            "topic": "strings",
            "title": "Valid Parentheses",
            "difficulty": "Easy",
            "status": "Completed",
            "date_solved": "2026-08-18"
        },
        headers=headers
    )
    
    response = client.get(
        "/analytics/weak-topics",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    # Check response structure
    for topic in data:
        assert "topic" in topic
        assert "completed" in topic
        assert "total" in topic
        assert "Solve_Rate" in topic
        assert "Soved_percentage" in topic


def test_user_isolation_analytics_only_own_data(client):
    """Auth boundary: users only see their own analytics."""
    # User A creates problems
    client.post(
        "/auth/register",
        json={"email": "anaA@example.com", "password": "TestPass123"}
    )
    login_a = client.post(
        "/auth/login",
        json={"email": "anaA@example.com", "password": "TestPass123"}
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    client.post(
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
    
    # User B creates different problems
    client.post(
        "/auth/register",
        json={"email": "anaB@example.com", "password": "TestPass123"}
    )
    login_b = client.post(
        "/auth/login",
        json={"email": "anaB@example.com", "password": "TestPass123"}
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    client.post(
        "/problems",
        json={
            "topic": "strings",
            "title": "User B Problem",
            "difficulty": "Easy",
            "status": "Completed",
            "date_solved": "2026-08-16"
        },
        headers=headers_b
    )
    
    # User A checks weak topics — should only see arrays
    response_a = client.get(
        "/analytics/weak-topics",
        headers=headers_a
    )
    data_a = response_a.json()
    
    # User B checks weak topics — should only see strings
    response_b = client.get(
        "/analytics/weak-topics",
        headers=headers_b
    )
    data_b = response_b.json()
    
    # Verify isolation
    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert len(data_a) == 1
    assert len(data_b) == 1
    assert data_a[0]["topic"] == "Arrays"
    assert data_b[0]["topic"] == "Strings"