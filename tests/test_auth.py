def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/auth/register",
        json={"email": "testuser@example.com", "password": "TestPassword123"}
    )
    
    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"


def test_register_duplicate_email(client):
    """Test registration fails with duplicate email."""
    email = "duplicate@example.com"
    password = "TestPassword123"
    
    # First registration should succeed
    response1 = client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    assert response1.status_code == 201
    
    # Second registration with same email should fail
    response2 = client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"]


def test_login_success(client):
    """Test successful login."""
    email = "logintest@example.com"
    password = "TestPassword123"
    
    # Register first
    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login fails with wrong password."""
    email = "wrongpass@example.com"
    password = "TestPassword123"
    
    # Register
    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "WrongPassword"}
    )
    
    assert response.status_code == 401
    assert "Invalid Credentials" in response.json()["detail"]