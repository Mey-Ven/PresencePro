import pytest
from fastapi.testclient import TestClient
from app.models import UserRole


def test_login_success(client: TestClient, admin_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin_test",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, admin_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin_test",
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_register_user_as_admin(client: TestClient, admin_user):
    """Test user registration by admin."""
    # First login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin_test",
            "password": "admin123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Register new user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "new_teacher",
            "password": "teacher123",
            "role": "enseignant",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@school.com"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_teacher"
    assert data["role"] == "enseignant"


def test_register_bulk_users(client: TestClient, admin_user):
    """Test bulk user registration."""
    # Login as admin
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin_test",
            "password": "admin123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create bulk users
    response = client.post(
        "/api/v1/auth/register/bulk",
        json={
            "role": "etudiant",
            "count": 3,
            "prefix": "class2024"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["users"]) == 3
    assert "warning" in data


def test_get_my_role(client: TestClient, student_user):
    """Test getting current user role."""
    # Login as student
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "student_test",
            "password": "student123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get role
    response = client.get(
        "/api/v1/auth/roles/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "etudiant"
    assert data["username"] == "student_test"


def test_check_roles(client: TestClient, student_user):
    """Test role checking."""
    # Login as student
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "student_test",
            "password": "student123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Check if student has admin role (should be false)
    response = client.post(
        "/api/v1/auth/roles/check",
        json={
            "required_roles": ["admin"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] == False
    assert data["current_role"] == "etudiant"


def test_refresh_token(client: TestClient, admin_user):
    """Test token refresh."""
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin_test",
            "password": "admin123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh-token",
        json={
            "refresh_token": refresh_token
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_unauthorized_access(client: TestClient):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/v1/auth/roles/me")
    assert response.status_code == 403


def test_insufficient_permissions(client: TestClient, student_user):
    """Test accessing admin-only endpoint as student."""
    # Login as student
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "student_test",
            "password": "student123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to register user (admin only)
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_user",
            "password": "test123",
            "role": "etudiant"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
