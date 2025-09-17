# AWS Health PHI Report Generator - Complete API Testing Guide

This document provides comprehensive test data for all API endpoints in the AWS Health PHI Report Generator v2.0.0.

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for testing.

---

# 🏠 **Default Endpoints**

## **GET** `/`
**Description:** Root endpoint with API information.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "message": "AWS Health PHI Report Generator is running",
  "version": "2.0.0",
  "docs_url": "/docs",
  "status": "healthy"
}
```

---

## **GET** `/health`
**Description:** Health check endpoint with database status.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/health' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-29T00:00:00Z",
  "database": "connected",
  "services": {
    "api": "running",
    "mongodb": "connected"
  }
}
```

---

## **GET** `/database/status`
**Description:** Get detailed database connection status.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/database/status' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "connected": true,
  "mongodb_url": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mt...",
  "database_name": "pha_connections",
  "connection_timeout_ms": 30000,
  "server_selection_timeout_ms": 30000
}
```

---

## **POST** `/database/reconnect`
**Description:** Manually trigger database reconnection.

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/database/reconnect' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "status": "success",
  "message": "Database reconnected successfully"
}
```

---

# 🔗 **Database Connections API**

## **GET** `/api/v1/connections/`
**Description:** Get all database connections.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/connections/' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
[
  {
    "_id": "68c15e54da77df2834036fa6",
    "connection_name": "Local MySQL",
    "database_type": "mysql",
    "connection_string": "mysql://user:pass@localhost:3306/testdb",
    "created_at": "2025-09-11T10:30:00Z",
    "updated_at": "2025-09-11T10:30:00Z"
  }
]
```

---

## **POST** `/api/v1/connections/`
**Description:** Create a new database connection.

### **Test Data - MySQL:**
```json
{
  "connection_name": "Test MySQL Connection",
  "database_type": "mysql",
  "connection_string": "mysql://testuser:testpass@localhost:3306/testdb",
  "additional_notes": "Test MySQL database for development",
  "host": "localhost",
  "port": 3306,
  "database_name": "testdb",
  "username": "testuser",
  "password": "testpass"
}
```

### **Test Data - PostgreSQL:**
```json
{
  "connection_name": "Test PostgreSQL Connection",
  "database_type": "postgresql", 
  "connection_string": "postgresql://postgres:password@localhost:5432/testdb",
  "additional_notes": "Test PostgreSQL database",
  "host": "localhost",
  "port": 5432,
  "database_name": "testdb",
  "username": "postgres",
  "password": "password"
}
```

### **Test Data - MongoDB:**
```json
{
  "connection_name": "Test MongoDB Atlas",
  "database_type": "mongodb",
  "connection_string": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA",
  "additional_notes": "MongoDB Atlas cluster",
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter"
}
```

### **Test Data - MariaDB:**
```json
{
  "connection_name": "Test MariaDB SkySQL",
  "database_type": "mariadb",
  "connection_string": "mariadb://user:pass@host.skysql.com:5001/database",
  "additional_notes": "MariaDB SkySQL cloud database",
  "host": "host.skysql.com",
  "port": 5001,
  "database_name": "database",
  "username": "user",
  "password": "pass"
}
```

### **Test Data - Oracle:**
```json
{
  "connection_name": "Test Oracle Connection",
  "database_type": "oracle",
  "connection_string": "oracle://user:pass@localhost:1521/ORCL",
  "additional_notes": "Oracle database",
  "host": "localhost",
  "port": 1521,
  "database_name": "ORCL",
  "username": "user",
  "password": "pass"
}
```

### **Test Data - SQL Server:**
```json
{
  "connection_name": "Test SQL Server Connection",
  "database_type": "mssql",
  "connection_string": "mssql://sa:Password123@localhost:1433/master",
  "additional_notes": "SQL Server database",
  "host": "localhost",
  "port": 1433,
  "database_name": "master",
  "username": "sa",
  "password": "Password123"
}
```

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/connections/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "connection_name": "Test MySQL Connection",
  "database_type": "mysql",
  "connection_string": "mysql://testuser:testpass@localhost:3306/testdb",
  "additional_notes": "Test MySQL database for development"
}'
```

---

## **GET** `/api/v1/connections/{connection_id}`
**Description:** Get a specific database connection by ID.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/connections/68c15e54da77df2834036fa6' \
  -H 'accept: application/json'
```

**Note:** Replace `68c15e54da77df2834036fa6` with actual connection ID from your database.

---

## **PUT** `/api/v1/connections/{connection_id}`
**Description:** Update an existing database connection.

### **Test Data:**
```json
{
  "connection_name": "Updated MySQL Connection",
  "database_type": "mysql",
  "connection_string": "mysql://updateduser:updatedpass@localhost:3306/updateddb",
  "additional_notes": "Updated test MySQL database",
  "host": "localhost",
  "port": 3306,
  "database_name": "updateddb",
  "username": "updateduser",
  "password": "updatedpass"
}
```

### **Test Request:**
```bash
curl -X 'PUT' \
  'http://localhost:8000/api/v1/connections/68c15e54da77df2834036fa6' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "connection_name": "Updated MySQL Connection",
  "database_type": "mysql",
  "connection_string": "mysql://updateduser:updatedpass@localhost:3306/updateddb"
}'
```

---

## **DELETE** `/api/v1/connections/{connection_id}`
**Description:** Delete a database connection.

### **Test Request:**
```bash
curl -X 'DELETE' \
  'http://localhost:8000/api/v1/connections/68c15e54da77df2834036fa6' \
  -H 'accept: application/json'
```

---

## **POST** `/api/v1/connections/{connection_id}/test`
**Description:** Test a database connection.

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/connections/68c15e54da77df2834036fa6/test' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "status": "success",
  "message": "Connection successful",
  "database_type": "mysql",
  "connection_time_ms": 234,
  "server_version": "8.0.33",
  "test_timestamp": "2025-09-11T10:30:00Z"
}
```

---

## **GET** `/api/v1/connections/{connection_id}/schema`
**Description:** Get database schema for a connection.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/connections/68c15e54da77df2834036fa6/schema' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "status": "success",
  "message": "Retrieved MySQL schema: 3 tables/views from connection string",
  "database_type": "mysql",
  "database_name": "testdb",
  "tables": [
    {
      "name": "users",
      "type": "table",
      "fields": [
        {
          "name": "id",
          "type": "INT(11)",
          "nullable": false,
          "default": "AUTO_INCREMENT"
        },
        {
          "name": "username",
          "type": "VARCHAR(50)",
          "nullable": false,
          "default": null
        }
      ],
      "row_count": 10
    }
  ],
  "unified_schema": {
    "database_info": {
      "name": "testdb",
      "type": "mysql",
      "version": "8.0.33"
    },
    "tables": [...]
  }
}
```

---

## **GET** `/api/v1/connections/{connection_id}/databases`
**Description:** List available databases for a connection.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/connections/68c15e54da77df2834036fa6/databases' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "status": "success",
  "databases": [
    "information_schema",
    "testdb",
    "mysql",
    "performance_schema"
  ],
  "database_count": 4
}
```

---

# � **MongoDB Schema Analysis API**

## **GET** `/api/v1/mongodb-schema/test`
**Description:** Health check endpoint for MongoDB schema analysis service.

### **Test Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/mongodb-schema/test' \
  -H 'accept: application/json'
```

### **Expected Response:**
```json
{
  "status": "healthy",
  "service": "MongoDB Schema Analysis",
  "timestamp": "2025-09-11T06:30:18.888760",
  "features": [
    "Direct MongoDB analysis",
    "MongoDB Atlas support",
    "Schema comparison",
    "Webhook notifications",
    "Real-time monitoring"
  ]
}
```

---

## **POST** `/api/v1/mongodb-schema/analyze-direct`
**Description:** Perform direct MongoDB schema analysis with comprehensive field type detection.

### **Test Data:**
```json
{
  "connection_string": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA",
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "sample_size": 10
}
```

### **Alternative Test Data (Minimal):**
```json
{
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "sample_size": 5
}
```

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/mongodb-schema/analyze-direct' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "connection_string": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA",
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "sample_size": 10
}'
```

### **Expected Response:**
```json
{
  "status": "success",
  "message": "Successfully analyzed X collections",
  "database_name": "pha_connections",
  "collections": [
    {
      "name": "database_connections",
      "document_count": 5,
      "fields": {
        "_id": {
          "name": "_id",
          "type": "objectId",
          "frequency": 5,
          "percentage": 100.0,
          "sample_values": ["ObjectId('...')"]
        }
      },
      "indexes": [...],
      "sample_documents": [...]
    }
  ],
  "analysis_timestamp": "2025-09-11T06:30:18Z",
  "schema_hash": "abc123def456"
}
```

---

## **POST** `/api/v1/mongodb-schema/test-atlas-connection`
**Description:** Test MongoDB Atlas connection with detailed diagnostics.

### **Test Data:**
```json
{
  "connection_string": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA",
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "timeout_ms": 30000
}
```

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/mongodb-schema/test-atlas-connection' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "connection_string": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA",
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "timeout_ms": 30000
}'
```

### **Expected Response:**
```json
{
  "status": "success",
  "connection_test": "passed",
  "server_info": {
    "version": "7.0.x",
    "isAtlas": true,
    "host": "pha.o1mtvpd.mongodb.net"
  },
  "database_exists": true,
  "collections_found": 3,
  "response_time_ms": 1250
}
```

---

## **POST** `/api/v1/mongodb-schema/webhook/test`
**Description:** Test webhook URL connectivity and response.

### **Test Data:**
```json
{
  "webhook_url": "https://httpbin.org/post",
  "timeout_seconds": 30
}
```

### **Alternative Test URLs:**
```json
{
  "webhook_url": "https://webhook.site/unique-id-here",
  "timeout_seconds": 15
}
```

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/mongodb-schema/webhook/test' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "webhook_url": "https://httpbin.org/post",
  "timeout_seconds": 30
}'
```

### **Expected Response:**
```json
{
  "status": "success",
  "webhook_url": "https://httpbin.org/post",
  "response_code": 200,
  "response_time_ms": 1234,
  "error_message": null,
  "test_timestamp": "2025-09-11T06:30:18.652Z"
}
```

---

## **POST** `/api/v1/mongodb-schema/webhook/notify`
**Description:** Send schema change notification to webhook URL.

### **Test Data:**
```json
{
  "webhook_url": "https://httpbin.org/post",
  "message": "Schema change detected in pha_connections database",
  "schema_data": {
    "database": "pha_connections",
    "collections_added": ["new_collection"],
    "fields_modified": ["database_connections.status"],
    "timestamp": "2025-09-11T06:30:18Z"
  },
  "change_type": "schema_change"
}
```

### **Alternative Test Data:**
```json
{
  "webhook_url": "https://webhook.site/your-unique-id",
  "message": "New collection added to database",
  "schema_data": {
    "database": "pha_connections",
    "event": "collection_added",
    "collection_name": "user_sessions"
  },
  "change_type": "collection_added"
}
```

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/mongodb-schema/webhook/notify' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "webhook_url": "https://httpbin.org/post",
  "message": "Schema change detected in pha_connections database",
  "schema_data": {
    "database": "pha_connections",
    "collections_added": ["new_collection"],
    "fields_modified": ["database_connections.status"]
  },
  "change_type": "schema_change"
}'
```

### **Expected Response:**
```json
{
  "status": "success",
  "message": "Notification sent successfully",
  "webhook_response": {
    "status_code": 200,
    "response_time_ms": 850
  }
}
```

---

## **POST** `/api/v1/mongodb-schema/schema/compare`
**Description:** Compare current schema with previous version using hash-based detection.

### **Test Data:**
```json
{
  "connection_string": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA",
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "previous_schema_hash": "abc123def456",
  "include_sample_data": true
}
```

### **Alternative Test Data (No Previous Hash):**
```json
{
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "previous_schema_hash": "",
  "include_sample_data": false
}
```

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/mongodb-schema/schema/compare' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "connection_string": "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA",
  "host": "pha.o1mtvpd.mongodb.net",
  "database_name": "pha_connections",
  "username": "22cs027_db_user",
  "password": "SathyaPainter",
  "is_atlas": true,
  "previous_schema_hash": "abc123def456",
  "include_sample_data": true
}'
```

### **Expected Response:**
```json
{
  "status": "success",
  "schema_changed": false,
  "current_hash": "xyz789abc012",
  "previous_hash": "abc123def456",
  "changes_detected": {
    "collections_added": [],
    "collections_removed": [],
    "fields_added": {},
    "fields_removed": {},
    "fields_modified": {}
  },
  "comparison_timestamp": "2025-09-11T06:30:18Z"
}
```

---

## **POST** `/api/v1/mongodb-schema/webhook-receiver`
**Description:** Receive and process webhook notifications.

### **Test Data:**
```json
{
  "event_type": "schema_change",
  "database": "pha_connections",
  "timestamp": "2025-09-11T06:30:18Z",
  "changes": {
    "collections_modified": ["database_connections"],
    "new_fields": ["last_used_timestamp"]
  },
  "source": "mongodb_atlas_trigger"
}
```

### **Alternative Test Data:**
```json
{
  "event_type": "collection_created",
  "database": "pha_connections",
  "collection_name": "user_sessions",
  "timestamp": "2025-09-11T06:30:18Z",
  "metadata": {
    "created_by": "system",
    "initial_document_count": 0
  }
}
```

### **Test Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/mongodb-schema/webhook-receiver' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "event_type": "schema_change",
  "database": "pha_connections",
  "timestamp": "2025-09-11T06:30:18Z",
  "changes": {
    "collections_modified": ["database_connections"],
    "new_fields": ["last_used_timestamp"]
  },
  "source": "mongodb_atlas_trigger"
}'
```

### **Expected Response:**
```json
{
  "status": "received",
  "message": "Webhook notification processed successfully",
  "processed_at": "2025-09-11T06:30:18Z",
  "event_id": "wh_12345"
}
```

---

## 🚀 **Quick Test Script**

### **PowerShell Test Script:**
```powershell
# Save this as test_mongodb_api.ps1

$baseUrl = "http://localhost:8000/api/v1/mongodb-schema"

# Test 1: Health Check
Write-Host "Testing Health Check..." -ForegroundColor Green
Invoke-RestMethod -Uri "$baseUrl/test" -Method GET

# Test 2: Analyze Direct
Write-Host "`nTesting Direct Analysis..." -ForegroundColor Green
$directData = @{
    connection_string = "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA"
    host = "pha.o1mtvpd.mongodb.net"
    database_name = "pha_connections"
    username = "22cs027_db_user"
    password = "SathyaPainter"
    is_atlas = $true
    sample_size = 10
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/analyze-direct" -Method POST -Body $directData -ContentType "application/json"

# Test 3: Webhook Test
Write-Host "`nTesting Webhook..." -ForegroundColor Green
$webhookData = @{
    webhook_url = "https://httpbin.org/post"
    timeout_seconds = 30
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/webhook/test" -Method POST -Body $webhookData -ContentType "application/json"
```

---

## 📝 **Notes:**

1. **Replace webhook URLs** with your actual webhook endpoints for real testing
2. **MongoDB credentials** are for testing only - use proper security in production
3. **Timeout values** may need adjustment based on network conditions
4. **Sample sizes** can be adjusted based on collection sizes
5. **Error handling** - All endpoints return proper HTTP status codes and error messages

---

## 🔧 **Troubleshooting:**

### **Common Issues:**
1. **DNS Resolution Error:** Check network connectivity and MongoDB Atlas whitelist
2. **Authentication Failed:** Verify username/password and database permissions
3. **Timeout Errors:** Increase timeout_ms values for slow connections
4. **Webhook Test Failures:** Ensure webhook URL is accessible and accepts POST requests

### **Debug Mode:**
Add `?debug=true` to any endpoint URL for verbose logging and detailed error messages.

---

## 📊 **Expected Performance:**
- **Health Check:** < 50ms
- **Direct Analysis:** 2-10 seconds (depends on collection sizes)
- **Atlas Connection Test:** 1-3 seconds
- **Webhook Tests:** 1-5 seconds
- **Schema Comparison:** 3-15 seconds (depends on complexity)

---

# 🚀 **Complete API Testing Scripts**

## **PowerShell Complete Test Script:**
```powershell
# Save this as complete_api_test.ps1

$baseUrl = "http://localhost:8000"
$mongoUrl = "$baseUrl/api/v1/mongodb-schema"
$connectionsUrl = "$baseUrl/api/v1/connections"

Write-Host "🚀 Testing AWS Health PHI Report Generator API v2.0.0" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Test 1: Root Health Check
Write-Host "`n1. Testing Root Endpoint..." -ForegroundColor Green
try {
    $result = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    Write-Host "✅ Root endpoint working: $($result.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Health Check
Write-Host "`n2. Testing Health Check..." -ForegroundColor Green
try {
    $result = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health check: $($result.status) - Database: $($result.database)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Database Status
Write-Host "`n3. Testing Database Status..." -ForegroundColor Green
try {
    $result = Invoke-RestMethod -Uri "$baseUrl/database/status" -Method GET
    Write-Host "✅ Database connected: $($result.connected)" -ForegroundColor Green
} catch {
    Write-Host "❌ Database status failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Create MySQL Connection
Write-Host "`n4. Testing Create MySQL Connection..." -ForegroundColor Green
$mysqlConnection = @{
    connection_name = "Test MySQL Connection $(Get-Date -Format 'HHmmss')"
    database_type = "mysql"
    connection_string = "mysql://testuser:testpass@localhost:3306/testdb"
    additional_notes = "Automated test connection"
    host = "localhost"
    port = 3306
    database_name = "testdb"
    username = "testuser"
    password = "testpass"
} | ConvertTo-Json

try {
    $newConnection = Invoke-RestMethod -Uri "$connectionsUrl/" -Method POST -Body $mysqlConnection -ContentType "application/json"
    $connectionId = $newConnection._id
    Write-Host "✅ MySQL connection created: $connectionId" -ForegroundColor Green
    
    # Test the created connection
    Write-Host "`n5. Testing Connection Test..." -ForegroundColor Green
    try {
        $testResult = Invoke-RestMethod -Uri "$connectionsUrl/$connectionId/test" -Method POST
        Write-Host "✅ Connection test: $($testResult.status)" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Connection test failed (expected - no actual MySQL server): $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Get connection details
    Write-Host "`n6. Testing Get Connection..." -ForegroundColor Green
    try {
        $connection = Invoke-RestMethod -Uri "$connectionsUrl/$connectionId" -Method GET
        Write-Host "✅ Retrieved connection: $($connection.connection_name)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Get connection failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Create connection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: MongoDB Schema Health Check
Write-Host "`n7. Testing MongoDB Schema Health..." -ForegroundColor Green
try {
    $result = Invoke-RestMethod -Uri "$mongoUrl/test" -Method GET
    Write-Host "✅ MongoDB Schema service: $($result.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ MongoDB Schema health failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: MongoDB Direct Analysis
Write-Host "`n8. Testing MongoDB Direct Analysis..." -ForegroundColor Green
$mongoData = @{
    connection_string = "mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA"
    host = "pha.o1mtvpd.mongodb.net"
    database_name = "pha_connections"
    username = "22cs027_db_user"
    password = "SathyaPainter"
    is_atlas = $true
    sample_size = 5
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$mongoUrl/analyze-direct" -Method POST -Body $mongoData -ContentType "application/json"
    Write-Host "✅ MongoDB analysis: $($result.status) - Found $($result.collections.Count) collections" -ForegroundColor Green
} catch {
    Write-Host "⚠️  MongoDB analysis may have connectivity issues: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 9: Webhook Test
Write-Host "`n9. Testing Webhook..." -ForegroundColor Green
$webhookData = @{
    webhook_url = "https://httpbin.org/post"
    timeout_seconds = 10
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$mongoUrl/webhook/test" -Method POST -Body $webhookData -ContentType "application/json"
    Write-Host "✅ Webhook test: $($result.status) - Response: $($result.response_code)" -ForegroundColor Green
} catch {
    Write-Host "❌ Webhook test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 10: Get All Connections
Write-Host "`n10. Testing Get All Connections..." -ForegroundColor Green
try {
    $connections = Invoke-RestMethod -Uri "$connectionsUrl/" -Method GET
    Write-Host "✅ Retrieved $($connections.Count) connections" -ForegroundColor Green
} catch {
    Write-Host "❌ Get all connections failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 API Testing Complete!" -ForegroundColor Cyan
Write-Host "Check individual test results above for any issues." -ForegroundColor Cyan
```

## **Bash Complete Test Script (Linux/Mac):**
```bash
#!/bin/bash
# Save this as complete_api_test.sh

BASE_URL="http://localhost:8000"
MONGO_URL="$BASE_URL/api/v1/mongodb-schema"
CONNECTIONS_URL="$BASE_URL/api/v1/connections"

echo "🚀 Testing AWS Health PHI Report Generator API v2.0.0"
echo "================================================="

# Test 1: Root endpoint
echo -e "\n1. Testing Root Endpoint..."
curl -s "$BASE_URL/" | jq '.'

# Test 2: Health check
echo -e "\n2. Testing Health Check..."
curl -s "$BASE_URL/health" | jq '.'

# Test 3: Database status
echo -e "\n3. Testing Database Status..."
curl -s "$BASE_URL/database/status" | jq '.'

# Test 4: Create connection
echo -e "\n4. Testing Create Connection..."
curl -X POST "$CONNECTIONS_URL/" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_name": "Test Connection",
    "database_type": "mysql",
    "connection_string": "mysql://test:test@localhost:3306/test"
  }' | jq '.'

# Test 5: MongoDB health
echo -e "\n5. Testing MongoDB Schema Health..."
curl -s "$MONGO_URL/test" | jq '.'

# Test 6: Webhook test
echo -e "\n6. Testing Webhook..."
curl -X POST "$MONGO_URL/webhook/test" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://httpbin.org/post",
    "timeout_seconds": 10
  }' | jq '.'

echo -e "\n🎉 Basic API Testing Complete!"
```

## **Quick Validation Checklist:**

### **✅ Basic Endpoints:**
- [ ] `GET /` - Root endpoint
- [ ] `GET /health` - Health check
- [ ] `GET /database/status` - Database status
- [ ] `POST /database/reconnect` - Database reconnect

### **✅ Database Connections:**
- [ ] `GET /api/v1/connections/` - List connections
- [ ] `POST /api/v1/connections/` - Create connection
- [ ] `GET /api/v1/connections/{id}` - Get connection
- [ ] `PUT /api/v1/connections/{id}` - Update connection
- [ ] `DELETE /api/v1/connections/{id}` - Delete connection
- [ ] `POST /api/v1/connections/{id}/test` - Test connection
- [ ] `GET /api/v1/connections/{id}/schema` - Get schema
- [ ] `GET /api/v1/connections/{id}/databases` - List databases

### **✅ MongoDB Schema Analysis:**
- [ ] `GET /api/v1/mongodb-schema/test` - Health check
- [ ] `POST /api/v1/mongodb-schema/analyze-direct` - Direct analysis
- [ ] `POST /api/v1/mongodb-schema/test-atlas-connection` - Test Atlas
- [ ] `POST /api/v1/mongodb-schema/webhook/test` - Test webhook
- [ ] `POST /api/v1/mongodb-schema/webhook/notify` - Send notification
- [ ] `POST /api/v1/mongodb-schema/schema/compare` - Compare schemas
- [ ] `POST /api/v1/mongodb-schema/webhook-receiver` - Receive webhook

---

## 📊 **Performance Expectations:**

| Endpoint Category | Expected Response Time | Notes |
|------------------|----------------------|-------|
| Health Checks | < 100ms | Quick status checks |
| Database Connections | 1-5 seconds | Depends on database latency |
| Schema Analysis | 5-30 seconds | Depends on database size |
| Webhook Operations | 1-10 seconds | Depends on network latency |

---

## 🔧 **Common Test Scenarios:**

### **1. New Installation Test:**
```bash
# Test basic functionality
curl localhost:8000/
curl localhost:8000/health
curl localhost:8000/database/status
```

### **2. Database Connectivity Test:**
```bash
# Create and test a connection
curl -X POST localhost:8000/api/v1/connections/ -H "Content-Type: application/json" -d '{"connection_name":"Test","database_type":"mysql","connection_string":"mysql://user:pass@host:3306/db"}'
# Use returned ID to test
curl -X POST localhost:8000/api/v1/connections/{id}/test
```

### **3. MongoDB Analysis Test:**
```bash
# Test MongoDB schema analysis
curl -X POST localhost:8000/api/v1/mongodb-schema/analyze-direct \
  -H "Content-Type: application/json" \
  -d '{"host":"pha.o1mtvpd.mongodb.net","database_name":"pha_connections","username":"22cs027_db_user","password":"SathyaPainter","is_atlas":true}'
```

---

*Last Updated: September 11, 2025*
