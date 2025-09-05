# PHA Database Connection Manager - API Documentation

## 🔗 Base URL
```
http://localhost:8000/api/v1
```

## 📊 API Endpoints

### 1. Create Database Connection
**Endpoint**: `POST /connections/`

**Description**: Create a new database connection configuration.

**Request Body**:
```json
{
  "connection_name": "string",
  "database_type": "string", 
  "host": "string",
  "port": integer,
  "database_name": "string",
  "username": "string",
  "password": "string",
  "additional_notes": "string (optional)"
}
```

**Example - MongoDB Atlas**:
```json
{
  "connection_name": "Production MongoDB",
  "database_type": "MongoDB",
  "host": "cluster0.mongodb.net",
  "port": 27017,
  "database_name": "production",
  "username": "dbuser",
  "password": "password123",
  "additional_notes": "Production Atlas cluster"
}
```

**Example - PostgreSQL Neon**:
```json
{
  "connection_name": "Neon PostgreSQL",
  "database_type": "PostgreSQL",
  "host": "ep-cool-math-123456.us-east-1.aws.neon.tech",
  "port": 5432,
  "database_name": "neondb",
  "username": "username",
  "password": "password",
  "additional_notes": "Neon cloud database"
}
```

**Response** (201 Created):
```json
{
  "id": "64f1a2b3c4d5e6f7g8h9i0j1",
  "connection_name": "Production MongoDB",
  "database_type": "MongoDB",
  "host": "cluster0.mongodb.net",
  "port": 27017,
  "database_name": "production",
  "username": "dbuser",
  "password": "password123",
  "additional_notes": "Production Atlas cluster",
  "created_at": "2025-09-02T10:30:00Z",
  "updated_at": "2025-09-02T10:30:00Z"
}
```

---

### 2. List All Connections
**Endpoint**: `GET /connections/`

**Description**: Retrieve all database connections.

**Response** (200 OK):
```json
[
  {
    "id": "64f1a2b3c4d5e6f7g8h9i0j1",
    "connection_name": "Production MongoDB",
    "database_type": "MongoDB",
    "host": "cluster0.mongodb.net",
    "port": 27017,
    "database_name": "production",
    "username": "dbuser",
    "password": "password123",
    "additional_notes": "Production Atlas cluster",
    "created_at": "2025-09-02T10:30:00Z",
    "updated_at": "2025-09-02T10:30:00Z"
  }
]
```

---

### 3. Get Connection by ID
**Endpoint**: `GET /connections/{connection_id}`

**Parameters**:
- `connection_id` (path): Database connection ID

**Response** (200 OK):
```json
{
  "id": "64f1a2b3c4d5e6f7g8h9i0j1",
  "connection_name": "Production MongoDB",
  "database_type": "MongoDB",
  "host": "cluster0.mongodb.net",
  "port": 27017,
  "database_name": "production",
  "username": "dbuser",
  "password": "password123",
  "additional_notes": "Production Atlas cluster",
  "created_at": "2025-09-02T10:30:00Z",
  "updated_at": "2025-09-02T10:30:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Connection not found"
}
```

---

### 4. Update Connection
**Endpoint**: `PUT /connections/{connection_id}`

**Parameters**:
- `connection_id` (path): Database connection ID

**Request Body** (all fields optional):
```json
{
  "connection_name": "Updated MongoDB",
  "database_type": "MongoDB",
  "host": "cluster1.mongodb.net",
  "port": 27017,
  "database_name": "staging",
  "username": "newuser",
  "password": "newpassword",
  "additional_notes": "Updated connection"
}
```

**Response** (200 OK):
```json
{
  "id": "64f1a2b3c4d5e6f7g8h9i0j1",
  "connection_name": "Updated MongoDB",
  "database_type": "MongoDB",
  "host": "cluster1.mongodb.net",
  "port": 27017,
  "database_name": "staging",
  "username": "newuser",
  "password": "newpassword",
  "additional_notes": "Updated connection",
  "created_at": "2025-09-02T10:30:00Z",
  "updated_at": "2025-09-02T11:15:00Z"
}
```

---

### 5. Delete Connection
**Endpoint**: `DELETE /connections/{connection_id}`

**Parameters**:
- `connection_id` (path): Database connection ID

**Response** (200 OK):
```json
{
  "message": "Connection deleted successfully"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Connection not found"
}
```

---

### 6. Test Connection
**Endpoint**: `POST /connections/test`

**Description**: Test if a database connection is working.

**Request Body**:
```json
{
  "connection_id": "64f1a2b3c4d5e6f7g8h9i0j1"
}
```

**Response - Success** (200 OK):
```json
{
  "status": "success",
  "message": "Connection successful"
}
```

**Response - Error** (200 OK):
```json
{
  "status": "error",
  "message": "Connection failed: Authentication error"
}
```

---

### 7. Extract Database Schema
**Endpoint**: `GET /connections/{connection_id}/schema`

**Description**: Extract and analyze database schema including tables/collections, fields, and types.

**Parameters**:
- `connection_id` (path): Database connection ID

#### MongoDB Schema Response:
```json
{
  "status": "success",
  "message": "Analyzed 5 collections with 1,250 total documents in database 'production'",
  "database_type": "MongoDB",
  "database_name": "production",
  "tables": [
    {
      "name": "users",
      "type": "collection",
      "fields": [
        {
          "name": "_id",
          "type": "ObjectId",
          "nullable": false,
          "default": "Present in 100.0% of documents"
        },
        {
          "name": "email",
          "type": "string",
          "nullable": true,
          "default": "Present in 95.2% of documents"
        },
        {
          "name": "profile",
          "type": "object",
          "nullable": true,
          "default": "Present in 87.3% of documents"
        },
        {
          "name": "profile.age",
          "type": "int",
          "nullable": true,
          "default": "Present in 82.1% of documents"
        },
        {
          "name": "tags",
          "type": "array[3]",
          "nullable": true,
          "default": "Present in 78.5% of documents"
        }
      ],
      "row_count": 1250
    },
    {
      "name": "orders",
      "type": "collection",
      "fields": [
        {
          "name": "_id",
          "type": "ObjectId",
          "nullable": false,
          "default": "Present in 100.0% of documents"
        },
        {
          "name": "user_id",
          "type": "ObjectId",
          "nullable": false,
          "default": "Present in 100.0% of documents"
        },
        {
          "name": "amount",
          "type": "double",
          "nullable": false,
          "default": "Present in 100.0% of documents"
        },
        {
          "name": "created_at",
          "type": "date",
          "nullable": false,
          "default": "Present in 100.0% of documents"
        }
      ],
      "row_count": 3420
    }
  ]
}
```

#### PostgreSQL Schema Response:
```json
{
  "status": "success",
  "message": "Retrieved schema for 8 tables/views",
  "database_type": "PostgreSQL",
  "database_name": "neondb",
  "tables": [
    {
      "name": "users",
      "type": "table",
      "fields": [
        {
          "name": "id",
          "type": "integer",
          "nullable": false,
          "default": "nextval('users_id_seq'::regclass)"
        },
        {
          "name": "email",
          "type": "character varying(255)",
          "nullable": false,
          "default": null
        },
        {
          "name": "created_at",
          "type": "timestamp with time zone",
          "nullable": true,
          "default": "CURRENT_TIMESTAMP"
        }
      ],
      "row_count": 1250
    },
    {
      "name": "orders",
      "type": "table",
      "fields": [
        {
          "name": "id",
          "type": "integer",
          "nullable": false,
          "default": "nextval('orders_id_seq'::regclass)"
        },
        {
          "name": "user_id",
          "type": "integer",
          "nullable": false,
          "default": null
        },
        {
          "name": "amount",
          "type": "numeric(10,2)",
          "nullable": false,
          "default": null
        }
      ],
      "row_count": 3420
    }
  ]
}
```

**Error Response** (200 OK):
```json
{
  "status": "error",
  "message": "Failed to analyze MongoDB collections: Authentication failed",
  "database_type": null,
  "database_name": null,
  "tables": null
}
```

---

### 8. Discover Available Databases
**Endpoint**: `GET /connections/{connection_id}/databases`

**Description**: List all available databases for a connection (MongoDB only).

**Parameters**:
- `connection_id` (path): Database connection ID

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Found 4 databases",
  "databases": [
    {
      "name": "production",
      "collections_count": 5,
      "collections": ["users", "orders", "products", "reviews", "analytics"]
    },
    {
      "name": "staging",
      "collections_count": 3,
      "collections": ["users", "orders", "products"]
    },
    {
      "name": "test",
      "collections_count": 0,
      "collections": []
    },
    {
      "name": "admin",
      "collections_count": 2,
      "collections": ["system.users", "system.version"]
    }
  ],
  "connection_info": {
    "host": "cluster0.mongodb.net",
    "username": "dbuser",
    "specified_database": "production"
  }
}
```

---

## 🔒 Authentication

Currently, the API does not require authentication. For production use, consider implementing:
- API key authentication
- JWT tokens
- OAuth 2.0

## 📝 Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Input validation failed |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Database connection issue |

## 📊 Rate Limiting

Currently no rate limiting is implemented. For production, consider:
- Request rate limiting per IP
- Connection attempt rate limiting
- Schema extraction frequency limits

## 🧪 Testing with cURL

### Create MongoDB Connection
```bash
curl -X POST "http://localhost:8000/api/v1/connections/" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_name": "Test MongoDB",
    "database_type": "MongoDB",
    "host": "cluster0.mongodb.net",
    "port": 27017,
    "database_name": "test",
    "username": "testuser",
    "password": "testpass",
    "additional_notes": "Test connection"
  }'
```

### Test Connection
```bash
curl -X POST "http://localhost:8000/api/v1/connections/test" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "64f1a2b3c4d5e6f7g8h9i0j1"
  }'
```

### Extract Schema
```bash
curl -X GET "http://localhost:8000/api/v1/connections/64f1a2b3c4d5e6f7g8h9i0j1/schema" \
  -H "Accept: application/json"
```

### List All Connections
```bash
curl -X GET "http://localhost:8000/api/v1/connections/" \
  -H "Accept: application/json"
```

## 🌐 Interactive Documentation

Access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Test all endpoints interactively
- View request/response schemas
- Download OpenAPI specification
- Generate client code

## 📱 Client SDKs

The API follows OpenAPI 3.0 specification, making it easy to generate client SDKs for various languages:

```bash
# Generate Python client
openapi-generator generate -i http://localhost:8000/openapi.json -g python -o ./python-client

# Generate JavaScript client  
openapi-generator generate -i http://localhost:8000/openapi.json -g javascript -o ./js-client

# Generate Java client
openapi-generator generate -i http://localhost:8000/openapi.json -g java -o ./java-client
```

---

**Last Updated**: September 2025  
**API Version**: 1.0.0  
**OpenAPI Specification**: 3.0.0
