"""
Tests for monitoring regions
"""
import pytest
from src.api.models import UserRole


@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Register and login
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
    
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword123"}
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_monitoring_region(client, auth_headers):
    """Test creating a monitoring region"""
    response = client.post(
        "/api/v1/regions/",
        json={
            "name": "Test Region",
            "description": "A test monitoring region",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius_km": 10.0
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Region"
    assert data["latitude"] == 40.7128
    assert data["is_active"] == True


def test_get_monitoring_regions(client, auth_headers):
    """Test getting all monitoring regions"""
    # Create a region first
    client.post(
        "/api/v1/regions/",
        json={
            "name": "Test Region",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius_km": 10.0
        },
        headers=auth_headers
    )
    
    response = client.get("/api/v1/regions/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Region"


def test_unauthorized_access(client):
    """Test unauthorized access to regions"""
    response = client.get("/api/v1/regions/")
    assert response.status_code == 401
