def test_create_company_success(client):
    """Happy path: create a valid company."""
    client.post(
        "/auth/register",
        json={"email": "comp1@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "comp1@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/companies",
        json={
            "name": "Zoho",
            "role": "Backend Intern",
            "interview_format": "Online + Technical",
            "application_status": "Applied"
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Zoho"
    assert data["role"] == "Backend Intern"
    assert data["application_status"] == "Applied"
    assert "id" in data
    assert "applied_on" in data


def test_create_company_invalid_status(client):
    """Validation: reject invalid application status."""
    client.post(
        "/auth/register",
        json={"email": "comp2@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "comp2@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/companies",
        json={
            "name": "Freshworks",
            "role": "SDE",
            "interview_format": "Remote",
            "application_status": "InvalidStatus"
        },
        headers=headers
    )
    
    assert response.status_code == 422


def test_update_company_status(client):
    """Happy path: update company application status."""
    client.post(
        "/auth/register",
        json={"email": "comp3@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "comp3@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create company
    create_response = client.post(
        "/companies",
        json={
            "name": "TCS Digital",
            "role": "Developer",
            "interview_format": "Online",
            "application_status": "Applied"
        },
        headers=headers
    )
    company_id = create_response.json()["id"]
    
    # Update status
    update_response = client.put(
        f"/companies/{company_id}",
        json={"application_status": "Interviewing"},
        headers=headers
    )
    
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["application_status"] == "Interviewing"
    assert "status_updated_at" in data


def test_user_isolation_cannot_delete_other_user_company(client):
    """Auth boundary: user cannot delete another user's companies."""
    # User A creates a company
    client.post(
        "/auth/register",
        json={"email": "compA@example.com", "password": "TestPass123"}
    )
    login_a = client.post(
        "/auth/login",
        json={"email": "compA@example.com", "password": "TestPass123"}
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    create_response = client.post(
        "/companies",
        json={
            "name": "User A Company",
            "role": "Developer",
            "interview_format": "Online",
            "application_status": "Applied"
        },
        headers=headers_a
    )
    company_id = create_response.json()["id"]
    
    # User B tries to delete User A's company
    client.post(
        "/auth/register",
        json={"email": "compB@example.com", "password": "TestPass123"}
    )
    login_b = client.post(
        "/auth/login",
        json={"email": "compB@example.com", "password": "TestPass123"}
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    response = client.delete(
        f"/companies/{company_id}",
        headers=headers_b
    )
    
    assert response.status_code == 404


def test_delete_nonexistent_company(client):
    """Not found: 404 for non-existent company."""
    client.post(
        "/auth/register",
        json={"email": "comp4@example.com", "password": "TestPass123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "comp4@example.com", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(
        "/companies/999999",
        headers=headers
    )
    
    assert response.status_code == 404