"""
Tests for authentication endpoints
"""
import pytest
from src.api.models import UserRole


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "organization": "Test Org",
            "role": UserRole.GOVERNMENT.value
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "password" not in data


def test_register_duplicate_user(client):
    """Test duplicate user registration"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "organization": "Test Org",
        "role": UserRole.GOVERNMENT.value
    }
    
    # Register first user
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register duplicate
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400


def test_login(client):
    """Test user login"""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "organization": "Test Org",
            "role": UserRole.GOVERNMENT.value
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "invalid", "password": "wrong"}
    )
    
    assert response.status_code == 401
