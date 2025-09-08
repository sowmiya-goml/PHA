# FHIR Integration System - Complete Documentation

## 🏥 Overview

This documentation covers the complete FHIR (Fast Healthcare Interoperability Resources) integration system built for the PHA application. The system implements Epic's OAuth2 Standalone Launch flow with full CRUD operations for managing multiple FHIR client configurations.

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [API Endpoints](#api-endpoints)
3. [Authentication Flow](#authentication-flow)
4. [Testing Guide](#testing-guide)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Architecture

The FHIR integration follows a layered architecture:

```
┌─────────────────────────────────────┐
│          Client Applications        │
│   (Web Browser, Mobile Apps, etc.)  │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         FastAPI Router Layer        │
│      (app/routers/fhir_connections)  │
│  • CRUD Endpoints                   │
│  • OAuth Flow Management            │
│  • Session Management               │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         Service Layer               │
│      (app/services/fhir_service)     │
│  • Business Logic                   │
│  • Token Management                 │
│  • FHIR API Calls                   │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         Model Layer                 │
│      (app/models/fhir_client)        │
│  • Data Structures                  │
│  • MongoDB Mapping                  │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         Database Layer              │
│         (MongoDB Atlas)              │
│  • Client Configurations            │
│  • Session Data                     │
│  • Token Storage                    │
└─────────────────────────────────────┘
```

### Key Components Created:

1. **Models** (`app/models/fhir_client.py`):
   - `FhirClientConfig`: Stores FHIR client configurations
   - `FhirSession`: Manages OAuth sessions and tokens

2. **Schemas** (`app/schemas/fhir.py`):
   - Request/Response validation using Pydantic
   - Security by excluding sensitive data

3. **Service** (`app/services/fhir_service.py`):
   - CRUD operations for client configurations
   - OAuth2 flow implementation
   - Session management
   - FHIR API calls

4. **Router** (`app/routers/fhir_connections.py`):
   - RESTful API endpoints
   - Error handling
   - Documentation

---

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/fhir`

### 1. Client Configuration Management

#### **POST** `/fhir/clients`
Create a new FHIR client configuration.

**Request Body:**
```json
{
  "client_id": "50560479-b540-428a-9b34-a8c49f51f0c0",
  "client_name": "Epic Sandbox Client",
  "client_secret": "Wui9fco0ArmvIvR/p9DPhXTMhPhpRDl0H19ABUBWHGx0ZOJWFUX4QnAQuCIlyx6BGRGAmT2/TAK5R4c757k2xg==",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/fhir/callback",
  "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read",
  "environment": "sandbox",
  "description": "Epic FHIR sandbox client for testing"
}
```

**Response:** `201 Created`
```json
{
  "client_id": "50560479-b540-428a-9b34-a8c49f51f0c0",
  "client_name": "Epic Sandbox Client",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/fhir/callback",
  "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read",
  "environment": "sandbox",
  "description": "Epic FHIR sandbox client for testing",
  "created_at": "2025-09-08T12:00:00Z",
  "updated_at": "2025-09-08T12:00:00Z"
}
```

#### **GET** `/fhir/clients`
List all FHIR client configurations.

**Response:** `200 OK`
```json
[
  {
    "client_id": "50560479-b540-428a-9b34-a8c49f51f0c0",
    "client_name": "Epic Sandbox Client",
    "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
    "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
    "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "redirect_uri": "http://localhost:8000/fhir/callback",
    "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read",
    "environment": "sandbox",
    "description": "Epic FHIR sandbox client for testing",
    "created_at": "2025-09-08T12:00:00Z",
    "updated_at": "2025-09-08T12:00:00Z"
  }
]
```

#### **GET** `/fhir/clients/{client_id}`
Get a specific FHIR client configuration.

#### **PUT** `/fhir/clients/{client_id}`
Update a FHIR client configuration.

#### **DELETE** `/fhir/clients/{client_id}`
Delete a FHIR client configuration and all associated sessions.

### 2. OAuth Flow Endpoints

#### **GET** `/fhir/authorize/{client_id}`
Start OAuth2 authorization flow.

**Response:** `200 OK`
```json
{
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize?response_type=code&client_id=50560479-b540-428a-9b34-a8c49f51f0c0&redirect_uri=http%3A//localhost%3A8000/fhir/callback&scope=openid+fhirUser+Patient.read+Patient.search+Practitioner.read&state=random_state_string&aud=https%3A//fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "state": "random_state_string",
  "session_id": "session_uuid",
  "client_name": "Epic Sandbox Client",
  "instructions": "Redirect user to the authorization_url to complete Epic Sandbox Client login"
}
```

#### **GET** `/fhir/callback`
Handle OAuth2 callback (automatically called by Epic).

**Query Parameters:**
- `code`: Authorization code from Epic
- `state`: Security state parameter

### 3. Session Management

#### **GET** `/fhir/sessions`
List all active FHIR sessions.

#### **GET** `/fhir/sessions/{session_id}/status`
Check session status.

#### **DELETE** `/fhir/sessions/{session_id}`
Disconnect a FHIR session.

### 4. FHIR Data Access

#### **GET** `/fhir/patient/{patient_id}?session_id={session_id}`
Get patient data using stored access token.

### 5. Utility Endpoints

#### **GET** `/fhir/clients/{client_id}/test`
Test connection to FHIR server without authentication.

#### **GET** `/fhir/`
API information and workflow guide.

---

## 🔐 Authentication Flow

### Step-by-Step OAuth2 Flow:

1. **Register Client Configuration**
   ```bash
   POST /fhir/clients
   # Register Epic client credentials
   ```

2. **Initiate OAuth Flow**
   ```bash
   GET /fhir/authorize/{client_id}
   # Get authorization URL
   ```

3. **User Authentication**
   - User is redirected to Epic's login page
   - User enters Epic sandbox credentials:
     - **Username:** `fhiruser`
     - **Password:** `epicepic1`

4. **Automatic Callback**
   ```bash
   GET /fhir/callback?code=AUTH_CODE&state=STATE
   # Epic automatically calls this endpoint
   ```

5. **Access FHIR Data**
   ```bash
   GET /fhir/patient/{patient_id}?session_id={session_id}
   # Use the session_id from step 4
   ```

---

## 🧪 Testing Guide

### Prerequisites

1. **Server Running:**
   ```bash
   cd backend
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Server should be running at: http://localhost:8000

2. **API Documentation:**
   Visit: http://localhost:8000/docs for interactive API documentation

### Epic Sandbox Configuration

Use these **exact values** for testing with Epic's sandbox:

```json
{
  "client_id": "50560479-b540-428a-9b34-a8c49f51f0c0",
  "client_name": "Epic Sandbox Test Client",
  "client_secret": "Wui9fco0ArmvIvR/p9DPhXTMhPhpRDl0H19ABUBWHGx0ZOJWFUX4QnAQuCIlyx6BGRGAmT2/TAK5R4c757k2xg==",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/fhir/callback",
  "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read",
  "environment": "sandbox",
  "description": "Epic FHIR sandbox client for testing"
}
```

### Testing Steps:

#### 1. Test Server Health
```bash
curl http://localhost:8000/health
```

#### 2. Test FHIR API Root
```bash
curl http://localhost:8000/fhir/
```

#### 3. Create FHIR Client Configuration
```bash
curl -X POST http://localhost:8000/fhir/clients \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "50560479-b540-428a-9b34-a8c49f51f0c0",
    "client_name": "Epic Sandbox Test Client",
    "client_secret": "Wui9fco0ArmvIvR/p9DPhXTMhPhpRDl0H19ABUBWHGx0ZOJWFUX4QnAQuCIlyx6BGRGAmT2/TAK5R4c757k2xg==",
    "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
    "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
    "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "redirect_uri": "http://localhost:8000/fhir/callback",
    "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read",
    "environment": "sandbox",
    "description": "Epic FHIR sandbox client for testing"
  }'
```

#### 4. List Client Configurations
```bash
curl http://localhost:8000/fhir/clients
```

#### 5. Test Connection
```bash
curl http://localhost:8000/fhir/clients/50560479-b540-428a-9b34-a8c49f51f0c0/test
```

#### 6. Start OAuth Flow
```bash
curl http://localhost:8000/fhir/authorize/50560479-b540-428a-9b34-a8c49f51f0c0
```

#### 7. Complete OAuth in Browser
1. Copy the `authorization_url` from step 6
2. Open it in a web browser
3. Login with Epic sandbox credentials:
   - **Username:** `fhiruser`
   - **Password:** `epicepic1`
4. You'll be redirected back to the callback endpoint
5. Note the `session_id` from the callback response

#### 8. Check Session Status
```bash
curl http://localhost:8000/fhir/sessions/{session_id}/status
```

#### 9. Get Patient Data
```bash
curl "http://localhost:8000/fhir/patient/eq081-VQEgP8drUUqCWzHfw3?session_id={session_id}"
```

### Test Patient IDs in Epic Sandbox:

- `eq081-VQEgP8drUUqCWzHfw3` - Demo patient
- `erXuFYUfucBZaryVksYEcMg3` - Another demo patient
- `eRicau0dVPAmiFlga-z-tQlbw93` - Another demo patient

---

## ⚙️ Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# Database Configuration
MONGODB_URL=mongodb+srv://your-mongodb-connection-string
DATABASE_NAME=pha_connections

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Performance Configuration
DB_CONNECTION_TIMEOUT_MS=10000
```

### Database Collections

The system creates these MongoDB collections:

1. **`fhir_clients`** - Stores FHIR client configurations
2. **`fhir_sessions`** - Stores OAuth sessions and tokens

---

## 🎯 Key Features Implemented

### ✅ **CRUD Operations for FHIR Clients**
- Create, Read, Update, Delete FHIR client configurations
- Multiple client support
- Secure storage (client secrets excluded from responses)

### ✅ **OAuth2 Flow Implementation**
- Epic's Standalone Launch flow
- State parameter for security
- Automatic token exchange
- Session management

### ✅ **Session Management**
- UUID-based sessions
- Token expiration handling
- Session status checking
- Clean disconnection

### ✅ **Security Features**
- State parameter validation
- Token encryption in storage
- Client secret protection
- Input validation with Pydantic

### ✅ **Error Handling**
- Comprehensive error responses
- HTTP status codes
- Detailed error messages
- Graceful failure handling

### ✅ **API Documentation**
- OpenAPI/Swagger documentation
- Request/response examples
- Interactive API testing
- Endpoint descriptions

---

## 🔧 Troubleshooting

### Common Issues:

#### 1. **"Client ID not found" Error**
- **Cause:** FHIR client not registered
- **Solution:** Create client configuration first using `POST /fhir/clients`

#### 2. **"Invalid state parameter" Error**
- **Cause:** OAuth state mismatch or session expired
- **Solution:** Start new OAuth flow with `GET /fhir/authorize/{client_id}`

#### 3. **"Token expired" Error**
- **Cause:** Access token has expired
- **Solution:** Start new OAuth flow to get fresh tokens

#### 4. **"Session not found" Error**
- **Cause:** Invalid session_id or session expired
- **Solution:** Check session status or start new OAuth flow

#### 5. **Database Connection Issues**
- **Cause:** MongoDB connection problems
- **Solution:** Check `MONGODB_URL` environment variable

### Debug Endpoints:

1. **Health Check:** `GET /health`
2. **FHIR API Info:** `GET /fhir/`
3. **Connection Test:** `GET /fhir/clients/{client_id}/test`
4. **Session List:** `GET /fhir/sessions`

---

## 📚 Additional Resources

### Epic FHIR Documentation:
- **Main Documentation:** https://fhir.epic.com/Documentation
- **OAuth2 Guide:** https://fhir.epic.com/Documentation?docId=oauth2
- **Sandbox Access:** https://fhir.epic.com/Developer

### API Testing Tools:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Postman Collection:** Available for import

### Epic Sandbox Credentials:
- **Username:** `fhiruser`
- **Password:** `epicepic1`
- **Environment:** Sandbox only

---

## 🎉 Summary

This FHIR integration system provides:

1. **Complete CRUD management** of FHIR client configurations
2. **Full OAuth2 implementation** following Epic's specifications
3. **Secure session management** with token storage
4. **Production-ready architecture** with proper error handling
5. **Comprehensive API documentation** with examples
6. **Easy testing workflow** with Epic's sandbox

The system is ready for production use and can be easily extended to support additional FHIR servers or custom workflows.

**Server Status:** ✅ Running at http://localhost:8000
**API Documentation:** ✅ Available at http://localhost:8000/docs
**Testing:** ✅ Ready with Epic sandbox credentials

---

*Last Updated: September 8, 2025*
*Version: 1.0.0*
