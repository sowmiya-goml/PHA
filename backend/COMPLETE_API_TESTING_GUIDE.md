# Complete FHIR API Testing Guide
*Testing all endpoints with /api/v1/fhir/ prefix*

## 🎯 Your Epic FHIR Credentials

**Client ID:** `57ec0583-7f79-41e0-850f-d7c9c7282178`
**Client Secret:** `RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==`
**Scopes:** `smart v1`
**Epic Login:** `fhiruser` / `epicepic1`

---

## 🚀 Complete API Testing Commands

### 📋 **1. FHIR Root - GET /api/v1/fhir/**
```bash
curl http://localhost:8000/api/v1/fhir/
```

### 👥 **2. Create FHIR Client - POST /api/v1/fhir/clients**
```bash
curl -X POST http://localhost:8000/api/v1/fhir/clients \
  -H "Content-Type: application/json" \
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

### 📄 **3. List FHIR Clients - GET /api/v1/fhir/clients**
```bash
curl http://localhost:8000/api/v1/fhir/clients
```

### 🔍 **4. Get Specific FHIR Client - GET /api/v1/fhir/clients/{client_id}**
```bash
curl http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178
```

### ✏️ **5. Update FHIR Client - PUT /api/v1/fhir/clients/{client_id}**
```bash
curl -X PUT http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178 \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Updated Epic Sandbox Client",
    "description": "Updated Epic FHIR sandbox client for testing"
  }'
```

### 🔌 **6. Test Client Connection - GET /api/v1/fhir/clients/{client_id}/test**
```bash
curl http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178/test
```

### 🔐 **7. Start OAuth Flow - GET /api/v1/fhir/authorize/{client_id}**
```bash
curl http://localhost:8000/api/v1/fhir/authorize/57ec0583-7f79-41e0-850f-d7c9c7282178
```

**Response will include:**
- `authorization_url` - Copy this and open in browser
- `session_id` - Save this for later steps

### 🌐 **8. OAuth Callback - GET /api/v1/fhir/callback**
This endpoint is called automatically by Epic after user login.
**Manual test URL format:**
```
http://localhost:8000/api/v1/fhir/callback?code=AUTH_CODE&state=STATE_VALUE
```

### 📊 **9. List FHIR Sessions - GET /api/v1/fhir/sessions**
```bash
curl http://localhost:8000/api/v1/fhir/sessions
```

### ✅ **10. Get Session Status - GET /api/v1/fhir/sessions/{session_id}/status**
```bash
curl http://localhost:8000/api/v1/fhir/sessions/YOUR_SESSION_ID/status
```
*Replace YOUR_SESSION_ID with actual session ID from step 7*

### 🏥 **11. Get Patient Data - GET /api/v1/fhir/patient/{patient_id}**
```bash
# Patient 1
curl "http://localhost:8000/api/v1/fhir/patient/eq081-VQEgP8drUUqCWzHfw3?session_id=YOUR_SESSION_ID"

# Patient 2  
curl "http://localhost:8000/api/v1/fhir/patient/erXuFYUfucBZaryVksYEcMg3?session_id=YOUR_SESSION_ID"

# Patient 3
curl "http://localhost:8000/api/v1/fhir/patient/eRicau0dVPAmiFlga-z-tQlbw93?session_id=YOUR_SESSION_ID"
```

### ❌ **12. Disconnect Session - DELETE /api/v1/fhir/sessions/{session_id}**
```bash
curl -X DELETE http://localhost:8000/api/v1/fhir/sessions/YOUR_SESSION_ID
```

### 🗑️ **13. Delete FHIR Client - DELETE /api/v1/fhir/clients/{client_id}**
```bash
curl -X DELETE http://localhost:8000/api/v1/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178
```

---

## 📋 **Step-by-Step Testing Workflow**

### **Phase 1: Setup**
1. ✅ Run command #1 (FHIR Root) - Test API is accessible
2. ✅ Run command #2 (Create Client) - Register your Epic credentials
3. ✅ Run command #3 (List Clients) - Verify client was created
4. ✅ Run command #6 (Test Connection) - Verify Epic connectivity

### **Phase 2: OAuth Flow**
5. ✅ Run command #7 (Start OAuth) - Get authorization URL and session_id
6. 🌐 Open authorization_url in browser
7. 🔐 Login with `fhiruser` / `epicepic1`
8. ✅ Click "Allow" to grant access
9. ↩️ Epic automatically calls callback endpoint
10. ✅ Run command #10 (Session Status) - Verify active session

### **Phase 3: Data Access**
11. ✅ Run command #11 (Get Patient Data) - Test FHIR data retrieval
12. ✅ Run command #9 (List Sessions) - See all active sessions

### **Phase 4: Management**
13. ✅ Run command #5 (Update Client) - Test client updates
14. ✅ Run command #4 (Get Client) - Verify updates
15. ✅ Run command #12 (Disconnect Session) - Clean up sessions
16. ✅ Run command #13 (Delete Client) - Clean up client

---

## 🔄 **Sample Response Examples**

### Create Client Response (201 Created):
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
  "created_at": "2025-09-08T12:00:00Z",
  "updated_at": "2025-09-08T12:00:00Z"
}
```

### Start OAuth Response (200 OK):
```json
{
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize?response_type=code&client_id=57ec0583-7f79-41e0-850f-d7c9c7282178&redirect_uri=http%3A//localhost%3A8000/api/v1/fhir/callback&scope=smart+v1&state=abc123&aud=https%3A//fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "state": "abc123",
  "session_id": "session-uuid-here",
  "client_name": "Epic Sandbox Test Client",
  "instructions": "Redirect user to the authorization_url to complete Epic Sandbox Test Client login"
}
```

### Session Status Response (200 OK):
```json
{
  "session_id": "session-uuid-here",
  "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
  "status": "active",
  "has_access_token": true,
  "token_expires_at": "2025-09-08T13:00:00Z",
  "created_at": "2025-09-08T12:00:00Z"
}
```

---

## 🎯 **Test Patient IDs for Epic Sandbox**

| Patient ID | Description |
|------------|-------------|
| `eq081-VQEgP8drUUqCWzHfw3` | Primary demo patient |
| `erXuFYUfucBZaryVksYEcMg3` | Secondary demo patient |
| `eRicau0dVPAmiFlga-z-tQlbw93` | Tertiary demo patient |

---

## 🐛 **Troubleshooting**

### Common Issues:

1. **404 Not Found**
   - Make sure you're using `/api/v1/fhir/` prefix in URLs
   - Verify server is running on port 8000

2. **Client not found**
   - Run command #2 first to create the client
   - Check client_id is correct

3. **OAuth login fails**
   - Use exact credentials: `fhiruser` / `epicepic1`
   - Make sure redirect_uri matches in client config

4. **Session expired**
   - Run command #7 to start new OAuth flow
   - Complete browser login process again

5. **Patient data access fails**
   - Verify session is active with command #10
   - Use correct session_id from OAuth flow

### Debug Commands:
```bash
# Check server health
curl http://localhost:8000/health

# Test FHIR root
curl http://localhost:8000/api/v1/fhir/

# List all clients
curl http://localhost:8000/api/v1/fhir/clients

# List all sessions  
curl http://localhost:8000/api/v1/fhir/sessions
```

---

## 🎉 **Quick Start Checklist**

- [ ] **Server Running**: Check http://localhost:8000
- [ ] **Create Client**: Run command #2
- [ ] **Start OAuth**: Run command #7  
- [ ] **Login Browser**: Use `fhiruser` / `epicepic1`
- [ ] **Grant Access**: Click "Allow" 
- [ ] **Test Patient**: Run command #11
- [ ] **Success**: You should get FHIR patient data! ✅

**All endpoints are ready for testing! 🚀**
