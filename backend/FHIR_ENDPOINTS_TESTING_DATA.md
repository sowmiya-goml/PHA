# FHIR API Testing Data - Complete Endpoint Collection

## 🏥 FHIR Integration - All Endpoints Testing Data

---

## 1. **GET** `/api/v1/fhir/`
**Fhir Root**

FHIR integration root endpoint with API information.

### Parameters
No parameters

### Curl Request
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/
```

### Expected Response (200)
```json
"FHIR Integration API - Root endpoint information"
```

---

## 2. **GET** `/api/v1/fhir/clients`
**List Fhir Clients**

Get all FHIR client configurations.

Returns a list of all registered FHIR clients (client secrets are excluded for security).

### Parameters
No parameters

### Curl Request
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/clients' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/clients
```

### Expected Response (200)
```json
[
  {
    "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
    "client_name": "Epic Sandbox Test Client",
    "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
    "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
    "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
    "scopes": "smart v1",
    "environment": "sandbox",
    "description": "Epic FHIR sandbox client for testing",
    "created_at": "2025-09-08T10:15:01.634Z",
    "updated_at": "2025-09-08T10:15:01.634Z"
  }
]
```

---

## 3. **POST** `/api/v1/fhir/clients`
**Create Fhir Client**

Create a new FHIR client configuration.

This endpoint allows you to register a new FHIR client with Epic or other FHIR servers. You need to provide the client credentials and endpoint URLs.

### Parameters
No parameters

### Request Body (application/json)
```json
{
  "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
  "client_name": "Epic Sandbox Test Client",
  "client_secret": "RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
  "scopes": "smart v1",
  "environment": "sandbox",
  "description": "Epic FHIR sandbox client for testing"
}
```

### Curl Request (Fixed JSON)
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/fhir/clients' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
    "client_name": "Epic Sandbox Test Client",
    "client_secret": "RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==",
    "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
    "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
    "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
    "scopes": "smart v1",
    "environment": "sandbox",
    "description": "Epic FHIR sandbox client for testing"
  }'
```

### ⚠️ **Common Error Fix**: 
The Swagger UI sometimes generates malformed curl commands missing `{` and `}`. Always ensure your JSON is properly formatted!

### Request URL
```
http://localhost:8000/api/v1/fhir/clients
```

### Expected Response (201)
```json
{
  "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
  "client_name": "Epic Sandbox Test Client",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
  "scopes": "smart v1",
  "environment": "sandbox",
  "description": "Epic FHIR sandbox client for testing",
  "created_at": "2025-09-08T10:15:01.636Z",
  "updated_at": "2025-09-08T10:15:01.636Z"
}
```

---

## 4. **GET** `/api/v1/fhir/clients/{client_id}`
**Get Fhir Client**

Get a specific FHIR client configuration by client ID.

### Parameters
- **client_id** (string, path, required): `57ec0583-7f79-41e0-850f-d7c9c7282178`

### Curl Request
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178
```

### Expected Response (200)
```json
{
  "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
  "client_name": "Epic Sandbox Test Client",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
  "scopes": "smart v1",
  "environment": "sandbox",
  "description": "Epic FHIR sandbox client for testing",
  "created_at": "2025-09-08T10:15:01.640Z",
  "updated_at": "2025-09-08T10:15:01.640Z"
}
```

---

## 5. **PUT** `/api/v1/fhir/clients/{client_id}`
**Update Fhir Client**

Update a FHIR client configuration.

### Parameters
- **client_id** (string, path, required): `57ec0583-7f79-41e0-850f-d7c9c7282178`

### Request Body (application/json)
```json
{
  "client_name": "Updated Epic Sandbox Test Client",
  "client_secret": "RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
  "scopes": "smart v1",
  "environment": "sandbox",
  "description": "Updated Epic FHIR sandbox client for testing"
}
```

### Curl Request
```bash
curl -X 'PUT' \
  'http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "client_name": "Updated Epic Sandbox Test Client",
    "client_secret": "RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==",
    "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
    "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
    "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
    "scopes": "smart v1",
    "environment": "sandbox",
    "description": "Updated Epic FHIR sandbox client for testing"
  }'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178
```

### Expected Response (200)
```json
{
  "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
  "client_name": "Updated Epic Sandbox Test Client",
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
  "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
  "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "redirect_uri": "http://localhost:8000/api/v1/fhir/callback",
  "scopes": "smart v1",
  "environment": "sandbox",
  "description": "Updated Epic FHIR sandbox client for testing",
  "created_at": "2025-09-08T10:15:01.644Z",
  "updated_at": "2025-09-08T10:15:01.644Z"
}
```

---

## 6. **DELETE** `/api/v1/fhir/clients/{client_id}`
**Delete Fhir Client**

Delete a FHIR client configuration and all associated sessions.

### Parameters
- **client_id** (string, path, required): `57ec0583-7f79-41e0-850f-d7c9c7282178`

### Curl Request
```bash
curl -X 'DELETE' \
  'http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178
```

### Expected Response (204)
```
No Content - Client successfully deleted
```

---

## 7. **GET** `/api/v1/fhir/authorize/{client_id}`
**Start Oauth Flow**

Initiate OAuth2 authorization flow for a specific FHIR client.

This endpoint starts the OAuth flow using the configuration of the specified client. The user will be redirected to the FHIR server's login page.

**Steps:**
1. Call this endpoint to get the authorization URL
2. Redirect the user to that URL in their browser
3. User logs in with Epic/FHIR credentials
4. User is redirected back to the callback endpoint automatically

### Parameters
- **client_id** (string, path, required): `57ec0583-7f79-41e0-850f-d7c9c7282178`

### Curl Request
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/authorize/57ec0583-7f79-41e0-850f-d7c9c7282178' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/authorize/57ec0583-7f79-41e0-850f-d7c9c7282178
```

### Expected Response (200)
```json
{
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize?response_type=code&client_id=57ec0583-7f79-41e0-850f-d7c9c7282178&redirect_uri=http%3A//localhost%3A8000/api/v1/fhir/callback&scope=smart+v1&state=abc123xyz&aud=https%3A//fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "state": "abc123xyz",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_name": "Epic Sandbox Test Client",
  "instructions": "Redirect user to the authorization_url to complete Epic Sandbox Test Client login"
}
```

---

## 8. **GET** `/api/v1/fhir/callback`
**Oauth Callback**

Handle OAuth2 callback from FHIR server and exchange code for access token.

This endpoint is called automatically by the FHIR server after user authentication. It exchanges the authorization code for an access token and creates a session.

This is the redirect_uri endpoint that you register with Epic/FHIR server.

### Parameters
- **code** (string, query, required): Authorization code from FHIR server
  - Example: `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9`
- **state** (string, query, required): State parameter for security validation
  - Example: `abc123xyz`

### Curl Request (Example)
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/callback?code=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9&state=abc123xyz' \
  -H 'accept: application/json'
```

### Request URL (Example)
```
http://localhost:8000/api/v1/fhir/callback?code=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9&state=abc123xyz
```

### Expected Response (200)
```json
{
  "message": "OAuth authorization successful - FHIR session established",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_name": "Epic Sandbox Test Client",
  "patient_id": "eq081-VQEgP8drUUqCWzHfw3",
  "expires_in": 3600,
  "scopes": "smart v1",
  "token_info": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer"
  }
}
```

---

## 9. **GET** `/api/v1/fhir/sessions`
**List Fhir Sessions**

Get all active FHIR sessions.

### Parameters
No parameters

### Curl Request
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/sessions' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/sessions
```

### Expected Response (200)
```json
[
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
    "client_name": "Epic Sandbox Test Client",
    "patient_id": "eq081-VQEgP8drUUqCWzHfw3",
    "expires_at": "2025-09-08T11:15:01.654Z",
    "scopes_granted": "smart v1",
    "is_expired": false,
    "created_at": "2025-09-08T10:15:01.654Z"
  }
]
```

---

## 10. **GET** `/api/v1/fhir/sessions/{session_id}/status`
**Get Session Status**

Check the status of a specific FHIR session.

### Parameters
- **session_id** (string, path, required): `550e8400-e29b-41d4-a716-446655440000`

### Curl Request
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/sessions/550e8400-e29b-41d4-a716-446655440000/status' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/sessions/550e8400-e29b-41d4-a716-446655440000/status
```

### Expected Response (200)
```json
{
  "connected": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_name": "Epic Sandbox Test Client",
  "patient_id": "eq081-VQEgP8drUUqCWzHfw3",
  "expires_at": "2025-09-08T11:15:01.656Z",
  "scopes": "smart v1",
  "is_expired": false
}
```

---

## 11. **DELETE** `/api/v1/fhir/sessions/{session_id}`
**Disconnect Session**

Disconnect a FHIR session by removing stored tokens.

### Parameters
- **session_id** (string, path, required): `550e8400-e29b-41d4-a716-446655440000`

### Curl Request
```bash
curl -X 'DELETE' \
  'http://localhost:8000/api/v1/fhir/sessions/550e8400-e29b-41d4-a716-446655440000' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/sessions/550e8400-e29b-41d4-a716-446655440000
```

### Expected Response (204)
```
No Content - Session successfully disconnected
```

---

## 12. **GET** `/api/v1/fhir/patient/{patient_id}`
**Get Patient Data**

Get patient data from FHIR server using stored access token.

### Parameters
- **patient_id** (string, path, required): `eq081-VQEgP8drUUqCWzHfw3`
- **session_id** (string, query, required): Session ID with valid access token
  - Example: `550e8400-e29b-41d4-a716-446655440000`

### Curl Request - Patient 1
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/patient/eq081-VQEgP8drUUqCWzHfw3?session_id=550e8400-e29b-41d4-a716-446655440000' \
  -H 'accept: application/json'
```

### Curl Request - Patient 2
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/patient/erXuFYUfucBZaryVksYEcMg3?session_id=550e8400-e29b-41d4-a716-446655440000' \
  -H 'accept: application/json'
```

### Curl Request - Patient 3
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/patient/eRicau0dVPAmiFlga-z-tQlbw93?session_id=550e8400-e29b-41d4-a716-446655440000' \
  -H 'accept: application/json'
```

### Request URL Examples
```
http://localhost:8000/api/v1/fhir/patient/eq081-VQEgP8drUUqCWzHfw3?session_id=550e8400-e29b-41d4-a716-446655440000
http://localhost:8000/api/v1/fhir/patient/erXuFYUfucBZaryVksYEcMg3?session_id=550e8400-e29b-41d4-a716-446655440000
http://localhost:8000/api/v1/fhir/patient/eRicau0dVPAmiFlga-z-tQlbw93?session_id=550e8400-e29b-41d4-a716-446655440000
```

### Expected Response (200)
```json
{
  "resourceType": "Patient",
  "id": "eq081-VQEgP8drUUqCWzHfw3",
  "identifier": [
    {
      "use": "usual",
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "MR"
          }
        ]
      },
      "system": "urn:oid:1.2.840.114350.1.13.0.1.7.5.737384.0",
      "value": "E4567"
    }
  ],
  "name": [
    {
      "use": "official",
      "family": "TestPatient",
      "given": ["Demo"]
    }
  ],
  "gender": "male",
  "birthDate": "1990-01-01"
}
```

---

## 13. **GET** `/api/v1/fhir/clients/{client_id}/test`
**Test Client Connection**

Test connection to FHIR server for a specific client without authentication.

### Parameters
- **client_id** (string, path, required): `57ec0583-7f79-41e0-850f-d7c9c7282178`

### Curl Request
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178/test' \
  -H 'accept: application/json'
```

### Request URL
```
http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178/test
```

### Expected Response (200)
```json
{
  "status": "success",
  "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
  "client_name": "Epic Sandbox Test Client",
  "status_code": 200,
  "server_info": {
    "resourceType": "CapabilityStatement",
    "id": "epic-r4-capability-statement",
    "status": "active",
    "date": "2024-01-01",
    "publisher": "Epic Systems Corporation"
  },
  "message": "Successfully connected to FHIR server",
  "error_details": null
}
```

---

## 🎯 **Epic Sandbox Test Credentials**

### **Client Configuration Data**
- **Client ID**: `57ec0583-7f79-41e0-850f-d7c9c7282178`
- **Client Secret**: `RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==`
- **Authorization URL**: `https://fhir.epic.com/Authorization/oauth2/authorize`
- **Token URL**: `https://fhir.epic.com/Authorization/oauth2/token`
- **FHIR Base URL**: `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4`
- **Redirect URI**: `http://localhost:8000/api/v1/fhir/callback`
- **Scopes**: `smart v1`

### **Epic Login Credentials**
- **Username**: `fhiruser`
- **Password**: `epicepic1`

### **Test Patient IDs**
- `eq081-VQEgP8drUUqCWzHfw3` (Primary demo patient)
- `erXuFYUfucBZaryVksYEcMg3` (Secondary demo patient)
- `eRicau0dVPAmiFlga-z-tQlbw93` (Tertiary demo patient)

---

## 🚀 **Quick Testing Workflow**

1. **Create Client** → Use endpoint #3 (POST /clients)
2. **Start OAuth** → Use endpoint #7 (GET /authorize/{client_id})
3. **Login Browser** → Open authorization_url, login with fhiruser/epicepic1
4. **Auto Callback** → Epic calls endpoint #8 automatically
5. **Test Data** → Use endpoint #12 with session_id to get patient data

**All endpoints ready for testing! 🎉**
