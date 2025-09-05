# PHA Database Connection Manager - Testing Guide

## 🧪 Testing Overview

This comprehensive testing guide covers all aspects of testing the PHA Database Connection Manager, from unit tests to end-to-end API testing.

---

## 🏗️ Test Structure

```
tests/
├── conftest.py                 # Test configuration and shared fixtures
├── test_connections.py         # API endpoint tests
├── test_models.py             # Model layer tests
├── test_services.py           # Service layer tests
├── test_database.py           # Database layer tests
├── test_schema_extraction.py  # Schema analysis tests
└── data/
    ├── sample_connections.json # Test data
    └── mock_responses.json     # Mock API responses
```

---

## 🚀 Quick Start Testing

### 1. **Setup Test Environment**

```bash
# Navigate to backend directory
cd backend

# Install dependencies with test extras
uv add --dev pytest pytest-asyncio pytest-mock httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_connections.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_create_connection"
```

### 2. **Environment Variables for Testing**

Create `.env.test` file:
```env
# Test Database (use separate test database)
MONGODB_URL=mongodb+srv://test_user:test_pass@test-cluster.mongodb.net/
DATABASE_NAME=pha_connections_test

# Test Configuration
TESTING=true
LOG_LEVEL=DEBUG
DB_CONNECTION_TIMEOUT_MS=5000
```

---

## 📋 Test Categories

### 1. **Unit Tests**

#### **Model Tests** (`test_models.py`)
```python
import pytest
from app.models.connection import DatabaseConnection

class TestDatabaseConnection:
    def test_connection_creation(self):
        """Test basic connection object creation."""
        connection = DatabaseConnection(
            connection_name="Test DB",
            database_type="MongoDB",
            host="localhost",
            port=27017,
            database_name="test_db",
            username="test_user",
            password="test_pass"
        )
        
        assert connection.connection_name == "Test DB"
        assert connection.database_type == "MongoDB"
        assert connection.host == "localhost"
        assert connection.port == 27017

    def test_to_dict_conversion(self):
        """Test model to dictionary conversion."""
        connection = DatabaseConnection(
            connection_name="Test DB",
            database_type="PostgreSQL",
            host="localhost",
            port=5432,
            database_name="test_db",
            username="test_user",
            password="test_pass"
        )
        
        result = connection.to_dict()
        
        assert result["connection_name"] == "Test DB"
        assert result["database_type"] == "PostgreSQL"
        assert "created_at" in result
        assert "updated_at" in result

    def test_from_dict_creation(self):
        """Test creating model from dictionary."""
        data = {
            "_id": "507f1f77bcf86cd799439011",
            "connection_name": "Test DB",
            "database_type": "MySQL",
            "host": "localhost",
            "port": 3306,
            "database_name": "test_db",
            "username": "test_user",
            "password": "test_pass"
        }
        
        connection = DatabaseConnection.from_dict(data)
        
        assert connection.id == "507f1f77bcf86cd799439011"
        assert connection.connection_name == "Test DB"
        assert connection.database_type == "MySQL"
```

#### **Service Tests** (`test_services.py`)
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.connection_service import ConnectionService

class TestConnectionService:
    @pytest.fixture
    def mock_db_manager(self):
        """Create mock database manager."""
        db_manager = MagicMock()
        db_manager.get_connections_collection.return_value = MagicMock()
        return db_manager

    @pytest.fixture
    def connection_service(self, mock_db_manager):
        """Create connection service with mocked database."""
        return ConnectionService(mock_db_manager)

    @pytest.mark.asyncio
    async def test_create_connection_success(self, connection_service, mock_db_manager):
        """Test successful connection creation."""
        # Mock data
        connection_data = {
            "connection_name": "Test DB",
            "database_type": "MongoDB",
            "host": "localhost",
            "port": 27017,
            "database_name": "test_db",
            "username": "test_user",
            "password": "test_pass"
        }
        
        # Mock database response
        mock_result = MagicMock()
        mock_result.inserted_id = "507f1f77bcf86cd799439011"
        mock_db_manager.get_connections_collection().insert_one.return_value = mock_result
        
        # Mock find_one for return
        mock_db_manager.get_connections_collection().find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            **connection_data,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        # Test creation
        result = await connection_service.create_connection(connection_data)
        
        assert result["id"] == "507f1f77bcf86cd799439011"
        assert result["connection_name"] == "Test DB"

    @pytest.mark.asyncio
    async def test_test_connection_mongodb_success(self, connection_service):
        """Test successful MongoDB connection testing."""
        with patch('pymongo.MongoClient') as mock_client:
            # Setup mock
            mock_instance = mock_client.return_value
            mock_instance.admin.command.return_value = {"ok": 1}
            
            connection = {
                "database_type": "MongoDB",
                "host": "localhost",
                "port": 27017,
                "username": "test_user",
                "password": "test_pass",
                "database_name": "test_db"
            }
            
            result = await connection_service._test_mongodb_connection(connection)
            
            assert result["success"] is True
            assert "Successfully connected to MongoDB" in result["message"]
```

### 2. **Integration Tests**

#### **Database Tests** (`test_database.py`)
```python
import pytest
from app.db.session import DatabaseManager
from app.core.config import settings

class TestDatabaseIntegration:
    @pytest.fixture
    async def db_manager(self):
        """Create database manager for testing."""
        # Use test database
        original_db_name = settings.DATABASE_NAME
        settings.DATABASE_NAME = "pha_connections_test"
        
        db_manager = DatabaseManager()
        yield db_manager
        
        # Cleanup: Drop test database
        db_manager.client.drop_database("pha_connections_test")
        settings.DATABASE_NAME = original_db_name

    @pytest.mark.asyncio
    async def test_database_connection(self, db_manager):
        """Test database connection establishment."""
        assert db_manager.is_connected() is True
        
        # Test collection access
        collection = db_manager.get_connections_collection()
        assert collection is not None

    @pytest.mark.asyncio
    async def test_crud_operations(self, db_manager):
        """Test basic CRUD operations."""
        collection = db_manager.get_connections_collection()
        
        # Insert test document
        test_doc = {
            "connection_name": "Integration Test DB",
            "database_type": "MongoDB",
            "host": "localhost",
            "port": 27017
        }
        
        result = collection.insert_one(test_doc)
        assert result.inserted_id is not None
        
        # Read document
        found_doc = collection.find_one({"_id": result.inserted_id})
        assert found_doc["connection_name"] == "Integration Test DB"
        
        # Update document
        collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"connection_name": "Updated Test DB"}}
        )
        
        updated_doc = collection.find_one({"_id": result.inserted_id})
        assert updated_doc["connection_name"] == "Updated Test DB"
        
        # Delete document
        delete_result = collection.delete_one({"_id": result.inserted_id})
        assert delete_result.deleted_count == 1
```

### 3. **API Tests**

#### **Endpoint Tests** (`test_connections.py`)
```python
import pytest
from httpx import AsyncClient
from app.main import app

class TestConnectionAPI:
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_create_connection_endpoint(self, client):
        """Test POST /connections endpoint."""
        connection_data = {
            "connection_name": "API Test DB",
            "database_type": "PostgreSQL",
            "host": "localhost",
            "port": 5432,
            "database_name": "test_db",
            "username": "test_user",
            "password": "test_pass",
            "additional_notes": "API testing"
        }
        
        response = await client.post("/connections/", json=connection_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["connection_name"] == "API Test DB"
        assert data["database_type"] == "PostgreSQL"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_all_connections(self, client):
        """Test GET /connections endpoint."""
        response = await client.get("/connections/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_connection_by_id(self, client):
        """Test GET /connections/{id} endpoint."""
        # First create a connection
        connection_data = {
            "connection_name": "Get Test DB",
            "database_type": "MongoDB",
            "host": "localhost",
            "port": 27017,
            "database_name": "test_db",
            "username": "test_user",
            "password": "test_pass"
        }
        
        create_response = await client.post("/connections/", json=connection_data)
        created_connection = create_response.json()
        connection_id = created_connection["id"]
        
        # Now get the connection
        response = await client.get(f"/connections/{connection_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == connection_id
        assert data["connection_name"] == "Get Test DB"

    @pytest.mark.asyncio
    async def test_test_connection_endpoint(self, client):
        """Test POST /connections/test endpoint."""
        connection_data = {
            "database_type": "MongoDB",
            "host": "localhost",
            "port": 27017,
            "database_name": "test_db",
            "username": "test_user",
            "password": "test_pass"
        }
        
        response = await client.post("/connections/test", json=connection_data)
        
        # Note: This will likely fail in test environment without actual database
        # Test should verify the response structure
        assert response.status_code in [200, 400]  # Success or connection failure
        data = response.json()
        assert "success" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_validation_errors(self, client):
        """Test input validation."""
        # Missing required fields
        invalid_data = {
            "connection_name": "",  # Empty name
            "database_type": "InvalidType",  # Invalid type
            "port": -1  # Invalid port
        }
        
        response = await client.post("/connections/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
```

### 4. **Schema Extraction Tests**

#### **Schema Analysis Tests** (`test_schema_extraction.py`)
```python
import pytest
from unittest.mock import patch, MagicMock
from app.services.connection_service import ConnectionService

class TestSchemaExtraction:
    @pytest.fixture
    def connection_service(self):
        """Create connection service with mocked database."""
        mock_db_manager = MagicMock()
        return ConnectionService(mock_db_manager)

    @pytest.mark.asyncio
    async def test_mongodb_schema_extraction(self, connection_service):
        """Test MongoDB schema extraction logic."""
        with patch('pymongo.MongoClient') as mock_client:
            # Setup mock MongoDB client
            mock_instance = mock_client.return_value
            mock_db = mock_instance.__getitem__.return_value
            
            # Mock collections
            mock_db.list_collection_names.return_value = ["users", "orders"]
            
            # Mock sample documents
            mock_collection = mock_db.__getitem__.return_value
            mock_collection.aggregate.return_value = [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "name": "John Doe",
                    "age": 30,
                    "email": "john@example.com",
                    "address": {
                        "street": "123 Main St",
                        "city": "New York",
                        "zip": "10001"
                    },
                    "tags": ["user", "premium"]
                },
                {
                    "_id": "507f1f77bcf86cd799439012",
                    "name": "Jane Smith",
                    "age": 25,
                    "email": "jane@example.com",
                    "is_active": True
                }
            ]
            
            connection = {
                "database_type": "MongoDB",
                "host": "localhost",
                "port": 27017,
                "username": "test_user",
                "password": "test_pass",
                "database_name": "test_db"
            }
            
            result = await connection_service._get_mongodb_schema(connection)
            
            assert "collections" in result
            assert len(result["collections"]) > 0
            
            # Verify field analysis
            users_collection = next(
                (c for c in result["collections"] if c["name"] == "users"), 
                None
            )
            assert users_collection is not None
            assert "fields" in users_collection

    @pytest.mark.asyncio
    async def test_postgresql_schema_extraction(self, connection_service):
        """Test PostgreSQL schema extraction logic."""
        with patch('psycopg2.connect') as mock_connect:
            # Setup mock PostgreSQL connection
            mock_conn = mock_connect.return_value
            mock_cursor = mock_conn.cursor.return_value
            
            # Mock schema query results
            mock_cursor.fetchall.side_effect = [
                # Tables query
                [
                    ("public", "users", "TABLE"),
                    ("public", "orders", "TABLE"),
                    ("public", "user_orders_view", "VIEW")
                ],
                # Columns query for users table
                [
                    ("id", "integer", "NO", "nextval('users_id_seq'::regclass)"),
                    ("name", "character varying", "NO", None),
                    ("email", "character varying", "YES", None),
                    ("created_at", "timestamp without time zone", "NO", "now()")
                ],
                # Columns query for orders table
                [
                    ("id", "integer", "NO", "nextval('orders_id_seq'::regclass)"),
                    ("user_id", "integer", "NO", None),
                    ("amount", "numeric", "NO", None),
                    ("status", "character varying", "NO", "'pending'::character varying")
                ]
            ]
            
            connection = {
                "database_type": "PostgreSQL",
                "host": "localhost",
                "port": 5432,
                "username": "test_user",
                "password": "test_pass",
                "database_name": "test_db"
            }
            
            result = await connection_service._get_postgresql_schema(connection)
            
            assert "tables" in result
            assert len(result["tables"]) == 2  # Only tables, not views
            assert "views" in result
            assert len(result["views"]) == 1

    def test_document_field_analysis(self, connection_service):
        """Test document field analysis logic."""
        documents = [
            {
                "name": "John",
                "age": 30,
                "email": "john@example.com",
                "address": {
                    "city": "New York",
                    "zip": "10001"
                },
                "tags": ["user", "premium"]
            },
            {
                "name": "Jane",
                "age": 25,
                "email": "jane@example.com",
                "is_active": True,
                "tags": ["user"]
            }
        ]
        
        fields = connection_service._analyze_document_fields(documents)
        
        # Check field types
        assert fields["name"]["type"] == "string"
        assert fields["age"]["type"] == "number"
        assert fields["email"]["type"] == "string"
        assert fields["address"]["type"] == "object"
        assert fields["tags"]["type"] == "array"
        assert fields["is_active"]["type"] == "boolean"
        
        # Check frequency
        assert fields["name"]["frequency"] == 1.0  # Present in all docs
        assert fields["is_active"]["frequency"] == 0.5  # Present in 50% of docs
```

---

## 🔧 Test Configuration

### **Pytest Configuration** (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
asyncio_mode = auto
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
    -v
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
```

### **Test Fixtures** (`conftest.py`)
```python
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.db.session import DatabaseManager
from app.core.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_client():
    """Create test client for API testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_db_manager():
    """Create test database manager."""
    # Use test database
    original_db_name = settings.DATABASE_NAME
    settings.DATABASE_NAME = "pha_connections_test"
    
    db_manager = DatabaseManager()
    yield db_manager
    
    # Cleanup
    db_manager.client.drop_database("pha_connections_test")
    settings.DATABASE_NAME = original_db_name

@pytest.fixture
def sample_connection_data():
    """Sample connection data for testing."""
    return {
        "connection_name": "Test Database",
        "database_type": "MongoDB",
        "host": "localhost",
        "port": 27017,
        "database_name": "test_db",
        "username": "test_user",
        "password": "test_pass",
        "additional_notes": "Test connection for unit testing"
    }

@pytest.fixture
def sample_connections_list():
    """Sample list of connections for testing."""
    return [
        {
            "connection_name": "MongoDB Test",
            "database_type": "MongoDB",
            "host": "localhost",
            "port": 27017,
            "database_name": "mongo_test",
            "username": "mongo_user",
            "password": "mongo_pass"
        },
        {
            "connection_name": "PostgreSQL Test",
            "database_type": "PostgreSQL",
            "host": "localhost",
            "port": 5432,
            "database_name": "postgres_test",
            "username": "postgres_user",
            "password": "postgres_pass"
        }
    ]
```

---

## 🚀 Running Tests

### **Basic Test Commands**

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio pytest-mock httpx pytest-cov

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_connections.py

# Run specific test method
pytest tests/test_connections.py::TestConnectionAPI::test_create_connection_endpoint

# Run tests with coverage
pytest --cov=app

# Run tests with HTML coverage report
pytest --cov=app --cov-report=html

# Run tests matching pattern
pytest -k "test_create"

# Run tests by marker
pytest -m "unit"
pytest -m "not slow"

# Run tests with debugging
pytest -s --pdb

# Run tests in parallel (with pytest-xdist)
pytest -n auto
```

### **Test Categories**

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# API tests only
pytest -m api

# Skip slow tests
pytest -m "not slow"

# Run specific database type tests
pytest -k "mongodb"
pytest -k "postgresql"
```

---

## 📊 Test Coverage

### **Coverage Requirements**
- **Minimum Coverage**: 85%
- **Critical Components**: 95%
- **Models**: 90%
- **Services**: 95%
- **APIs**: 90%

### **Coverage Commands**
```bash
# Generate coverage report
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI/CD)
pytest --cov=app --cov-report=xml

# Coverage with branch analysis
pytest --cov=app --cov-branch --cov-report=term-missing
```

---

## 🔍 Manual Testing

### **API Testing with cURL**

```bash
# Create connection
curl -X POST "http://localhost:8000/connections/" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_name": "Manual Test DB",
    "database_type": "MongoDB",
    "host": "localhost",
    "port": 27017,
    "database_name": "test_db",
    "username": "test_user",
    "password": "test_pass"
  }'

# Get all connections
curl -X GET "http://localhost:8000/connections/"

# Test connection
curl -X POST "http://localhost:8000/connections/test" \
  -H "Content-Type: application/json" \
  -d '{
    "database_type": "MongoDB",
    "host": "cluster0.mongodb.net",
    "port": 27017,
    "database_name": "sample_db",
    "username": "username",
    "password": "password"
  }'

# Get schema
curl -X GET "http://localhost:8000/connections/{connection_id}/schema"
```

### **Swagger UI Testing**
1. Start the application: `uvicorn app.main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Test each endpoint using the interactive interface
4. Verify request/response formats
5. Test error scenarios

---

## 🐛 Debugging Tests

### **Debug Failing Tests**
```bash
# Run with debugging
pytest -s --pdb

# Run single test with debugging
pytest tests/test_connections.py::test_create_connection -s --pdb

# Run with print statements
pytest -s

# Increase logging level
pytest --log-cli-level=DEBUG
```

### **Common Issues**

1. **Database Connection Issues**
   ```python
   # Mock database connections in tests
   @patch('pymongo.MongoClient')
   def test_mongodb_connection(mock_client):
       # Test logic here
   ```

2. **Async Test Issues**
   ```python
   # Ensure proper async test setup
   @pytest.mark.asyncio
   async def test_async_function():
       # Test async code
   ```

3. **Test Data Cleanup**
   ```python
   # Use fixtures for cleanup
   @pytest.fixture
   def setup_and_teardown():
       # Setup
       yield
       # Cleanup
   ```

---

## 📋 Test Checklist

### **Before Committing**
- [ ] All tests pass
- [ ] Code coverage above 85%
- [ ] No test warnings
- [ ] Integration tests pass
- [ ] API tests pass
- [ ] Performance tests pass

### **Before Deployment**
- [ ] Full test suite passes
- [ ] Integration tests with real databases
- [ ] Load testing completed
- [ ] Security testing completed
- [ ] API documentation tests pass

---

## 🚀 Continuous Integration

### **GitHub Actions Example**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install uv
        uv sync --dev
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

**Last Updated**: September 2025  
**Testing Guide Version**: 1.0.0  
**Documentation Status**: Complete
