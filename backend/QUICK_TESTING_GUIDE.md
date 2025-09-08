# FHIR Integration - Quick Testing Guide

## 🚀 Quick Start Testing

### Prerequisites
- Server running at: http://localhost:8000
- MongoDB connected
- Epic sandbox credentials ready

## 📋 Step-by-Step Testing Commands

### 1. Check Server Health
```bash
curl http://localhost:8000/health
```

### 2. Check FHIR API Info
```bash
curl http://localhost:8000/fhir/
```

### 3. Create Epic FHIR Client Configuration
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

**Expected Response:** `201 Created` with client details (no client_secret shown)

### 4. List All Clients
```bash
curl http://localhost:8000/fhir/clients
```

### 5. Test Connection to Epic FHIR Server
```bash
curl http://localhost:8000/fhir/clients/50560479-b540-428a-9b34-a8c49f51f0c0/test
```

### 6. Start OAuth Flow
```bash
curl http://localhost:8000/fhir/authorize/50560479-b540-428a-9b34-a8c49f51f0c0
```

**Expected Response:**
```json
{
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize?response_type=code&client_id=50560479-b540-428a-9b34-a8c49f51f0c0&redirect_uri=http%3A//localhost%3A8000/fhir/callback&scope=openid+fhirUser+Patient.read+Patient.search+Practitioner.read&state=RANDOM_STATE&aud=https%3A//fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "state": "RANDOM_STATE_STRING",
  "session_id": "SESSION_UUID",
  "client_name": "Epic Sandbox Test Client",
  "instructions": "Redirect user to the authorization_url to complete Epic Sandbox Test Client login"
}
```

### 7. Complete OAuth in Browser
1. **Copy the `authorization_url`** from step 6 response
2. **Open it in your web browser**
3. **Login with Epic sandbox credentials:**
   - Username: `fhiruser`
   - Password: `epicepic1`
4. **You'll be redirected** to: `http://localhost:8000/fhir/callback?code=...&state=...`
5. **Note the `session_id`** from the callback response

### 8. Check Session Status
```bash
curl http://localhost:8000/fhir/sessions/YOUR_SESSION_ID/status
```

### 9. List All Sessions
```bash
curl http://localhost:8000/fhir/sessions
```

### 10. Get Patient Data (Replace SESSION_ID)
```bash
curl "http://localhost:8000/fhir/patient/eq081-VQEgP8drUUqCWzHfw3?session_id=YOUR_SESSION_ID"
```

## 🎯 Test Patient IDs in Epic Sandbox

Use these patient IDs for testing:
- `eq081-VQEgP8drUUqCWzHfw3` - Demo patient 1
- `erXuFYUfucBZaryVksYEcMg3` - Demo patient 2
- `eRicau0dVPAmiFlga-z-tQlbw93` - Demo patient 3

## 📝 Configuration Values for Testing

### Epic FHIR Sandbox Configuration:
- **Client ID:** `50560479-b540-428a-9b34-a8c49f51f0c0`
- **Client Secret:** `Wui9fco0ArmvIvR/p9DPhXTMhPhpRDl0H19ABUBWHGx0ZOJWFUX4QnAQuCIlyx6BGRGAmT2/TAK5R4c757k2xg==`
- **Authorization URL:** `https://fhir.epic.com/Authorization/oauth2/authorize`
- **Token URL:** `https://fhir.epic.com/Authorization/oauth2/token`
- **FHIR Base URL:** `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4`
- **Redirect URI:** `http://localhost:8000/fhir/callback`

### Epic Sandbox Login Credentials:
- **Username:** `fhiruser`
- **Password:** `epicepic1`

## 🧪 Testing Workflow Summary

1. ✅ **Create client configuration** → Store Epic credentials
2. ✅ **Test connection** → Verify Epic server is reachable
3. ✅ **Start OAuth flow** → Get authorization URL
4. ✅ **Login in browser** → Use Epic sandbox credentials
5. ✅ **Get session ID** → From callback response
6. ✅ **Access patient data** → Using session ID

## 🔧 Troubleshooting Quick Checks

### If OAuth fails:
```bash
# Check if client exists
curl http://localhost:8000/fhir/clients/50560479-b540-428a-9b34-a8c49f51f0c0

# Test connection
curl http://localhost:8000/fhir/clients/50560479-b540-428a-9b34-a8c49f51f0c0/test
```

### If patient data fails:
```bash
# Check session status
curl http://localhost:8000/fhir/sessions/YOUR_SESSION_ID/status

# List all sessions
curl http://localhost:8000/fhir/sessions
```

## 🌐 Browser Testing

For interactive testing:
- **Swagger UI:** http://localhost:8000/docs
- **API Root:** http://localhost:8000/fhir/

## 📞 Support

If you encounter issues:
1. Check server logs in terminal
2. Verify MongoDB connection
3. Ensure Epic sandbox credentials are correct
4. Check redirect URI matches exactly: `http://localhost:8000/fhir/callback`

---

*Ready to test! Start with step 1 and follow sequentially.*
