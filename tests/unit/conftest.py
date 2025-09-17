"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_connection_data():
    """Sample connection data for testing."""
    return {
        "connection_name": "Test MySQL Connection",
        "database_type": "MySQL",
        "host": "localhost",
        "port": 3306,
        "database_name": "test_db",
        "username": "test_user",
        "password": "test_password",
        "additional_notes": "Test connection for unit tests"
    }
