"""Test cases for database connection API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["status"] == "healthy"
 

def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_create_connection_invalid_data(client: TestClient):
    """Test creating a connection with invalid data."""
    invalid_data = {
        "connection_name": "",  # Empty name should fail
        "database_type": "MySQL"
    }
    response = client.post("/api/v1/connections/", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_get_nonexistent_connection(client: TestClient):
    """Test getting a connection that doesn't exist."""
    response = client.get("/api/v1/connections/507f1f77bcf86cd799439011")
    # This might return 503 if database is not connected or 404 if connected
    assert response.status_code in [404, 503]


# Note: The following tests would require a working database connection
# and should be implemented as integration tests

# def test_create_connection_success(client: TestClient, sample_connection_data):
#     """Test successfully creating a connection."""
#     response = client.post("/api/v1/connections/", json=sample_connection_data)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["connection_name"] == sample_connection_data["connection_name"]
#     assert "id" in data
#     assert "created_at" in data

# def test_get_all_connections(client: TestClient):
#     """Test getting all connections."""
#     response = client.get("/api/v1/connections/")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)
