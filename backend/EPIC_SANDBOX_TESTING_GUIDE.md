# Epic FHIR Sandbox Testing Guide
*Complete step-by-step testing with your credentials*

## 🎯 Your Epic FHIR Credentials

**Client ID:** `57ec0583-7f79-41e0-850f-d7c9c7282178`
**Client Secret:** `RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==`
**Scopes:** `smart v1`
**Epic Sandbox Login:** Username: `fhiruser` | Password: `epicepic1`

---

## 🚀 Complete Testing Workflow

### Step 1: Register Your Epic Client Configuration

```bash
curl -X POST http://localhost:8000/fhir/clients \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
    "client_name": "Epic Sandbox Test Client",
    "client_secret": "RpTzlJYFjt0EW7KoSjODsDjWZu0/Q56bYPNWzqOTR/ipMD7UJWNAX5nkyCtdNIfDMFJ56c0Cp0AebIPGpRRc7A==",
    "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
    "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
    "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "redirect_uri": "http://localhost:8000/fhir/callback",
    "scopes": "smart v1",
    "environment": "sandbox",
    "description": "Epic FHIR sandbox client for testing"
  }'
```

**Expected Response:** ✅ `201 Created`

### Step 2: Verify Client Registration

```bash
curl http://localhost:8000/fhir/clients
```

**Expected Response:** List of registered clients including yours

### Step 3: Test Connection (Optional)

```bash
curl http://localhost:8000/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178/test
```

**Expected Response:** Basic connectivity test to Epic's FHIR server

### Step 4: Start OAuth Authorization Flow

```bash
curl http://localhost:8000/fhir/authorize/57ec0583-7f79-41e0-850f-d7c9c7282178
```

**Expected Response:**
```json
{
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize?response_type=code&client_id=57ec0583-7f79-41e0-850f-d7c9c7282178&redirect_uri=http%3A//localhost%3A8000/fhir/callback&scope=smart+v1&state=RANDOM_STATE&aud=https%3A//fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
  "state": "RANDOM_STATE",
  "session_id": "SESSION_UUID",
  "client_name": "Epic Sandbox Test Client",
  "instructions": "Redirect user to the authorization_url to complete Epic Sandbox Test Client login"
}
```

### Step 5: Complete OAuth in Browser

1. **Copy the `authorization_url`** from Step 4 response
2. **Open it in your web browser**
3. **Login with Epic sandbox credentials:**
   - Username: `fhiruser`
   - Password: `epicepic1`
4. **You'll be automatically redirected** to `http://localhost:8000/fhir/callback?code=AUTH_CODE&state=STATE`
5. **Note the `session_id`** from the response

### Step 6: Check Session Status

```bash
curl "http://localhost:8000/fhir/sessions/SESSION_ID/status"
```
*Replace SESSION_ID with the session_id from Step 5*

**Expected Response:**
```json
{
  "session_id": "SESSION_UUID",
  "client_id": "57ec0583-7f79-41e0-850f-d7c9c7282178",
  "status": "active",
  "has_access_token": true,
  "token_expires_at": "2025-09-08T13:00:00Z",
  "created_at": "2025-09-08T12:00:00Z"
}
```

### Step 7: Access FHIR Patient Data

Test with Epic sandbox patient IDs:

```bash
# Patient 1
curl "http://localhost:8000/fhir/patient/eq081-VQEgP8drUUqCWzHfw3?session_id=SESSION_ID"

# Patient 2
curl "http://localhost:8000/fhir/patient/erXuFYUfucBZaryVksYEcMg3?session_id=SESSION_ID"

# Patient 3
curl "http://localhost:8000/fhir/patient/eRicau0dVPAmiFlga-z-tQlbw93?session_id=SESSION_ID"
```

**Expected Response:** Full FHIR Patient resource JSON

---

## 🔧 All Available API Endpoints

### Health & Info Endpoints
```bash
# Server health check
curl http://localhost:8000/health

# FHIR API information
curl http://localhost:8000/fhir/

# Interactive API documentation
# Open in browser: http://localhost:8000/docs
```

### Client Management Endpoints
```bash
# Create client (Step 1 above)
POST http://localhost:8000/fhir/clients

# List all clients
GET http://localhost:8000/fhir/clients

# Get specific client
GET http://localhost:8000/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178

# Update client
PUT http://localhost:8000/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178

# Delete client
DELETE http://localhost:8000/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178

# Test connection
GET http://localhost:8000/fhir/clients/57ec0583-7f79-41e0-850f-d7c9c7282178/test
```

### OAuth Flow Endpoints
```bash
# Start OAuth flow
GET http://localhost:8000/fhir/authorize/57ec0583-7f79-41e0-850f-d7c9c7282178

# OAuth callback (automatically called by Epic)
GET http://localhost:8000/fhir/callback?code=AUTH_CODE&state=STATE
```

### Session Management
```bash
# List all sessions
GET http://localhost:8000/fhir/sessions

# Check session status
GET http://localhost:8000/fhir/sessions/SESSION_ID/status

# Disconnect session
DELETE http://localhost:8000/fhir/sessions/SESSION_ID
```

### FHIR Data Access
```bash
# Get patient data
GET http://localhost:8000/fhir/patient/PATIENT_ID?session_id=SESSION_ID
```

---

## 🔐 Epic Sandbox Access Grant Process

### How OAuth Works with Epic Sandbox:

1. **Your app redirects** user to Epic's authorization URL
2. **User logs in** with sandbox credentials (`fhiruser` / `epicepic1`)
3. **Epic shows consent screen** asking user to grant your app access
4. **User clicks "Allow"** to grant access
5. **Epic redirects back** to your callback with authorization code
6. **Your app exchanges** code for access token automatically
7. **Access token allows** FHIR API calls

### What Happens During Login:

1. **Login Screen**: User enters `fhiruser` / `epicepic1`
2. **Consent Screen**: Epic shows what data your app wants to access
3. **Grant Access**: User clicks "Allow" or "Authorize"
4. **Redirect**: Epic sends user back to your app with access code

### If Access is Denied:
- User clicks "Deny" → Epic redirects with error
- Your app receives error in callback URL
- No access token is issued

---

## 📋 Test Patient IDs for Epic Sandbox

Use these patient IDs for testing:

| Patient ID | Description |
|------------|-------------|
| `eq081-VQEgP8drUUqCWzHfw3` | Primary demo patient |
| `erXuFYUfucBZaryVksYEcMg3` | Secondary demo patient |
| `eRicau0dVPAmiFlga-z-tQlbw93` | Tertiary demo patient |

---

## 🐛 Troubleshooting

### Common Issues:

1. **"Client not found" error**
   - Run Step 1 first to register your client

2. **"Invalid state parameter" error**
   - Start fresh OAuth flow from Step 4

3. **OAuth login fails**
   - Use exact credentials: `fhiruser` / `epicepic1`
   - Make sure you're using Epic's sandbox, not production

4. **Session expired**
   - Start new OAuth flow (Steps 4-5)

5. **Patient not found**
   - Use the exact patient IDs provided above

### Debug Commands:
```bash
# Check if server is running
curl http://localhost:8000/health

# List all registered clients
curl http://localhost:8000/fhir/clients

# List all active sessions
curl http://localhost:8000/fhir/sessions

# Check specific session status
curl http://localhost:8000/fhir/sessions/SESSION_ID/status
```

---

## 🎯 Complete Testing Checklist

- [ ] **Step 1**: Register client configuration ✅
- [ ] **Step 2**: Verify client is listed ✅
- [ ] **Step 3**: Test basic connection ✅
- [ ] **Step 4**: Start OAuth flow ✅
- [ ] **Step 5**: Complete login in browser ✅
- [ ] **Step 6**: Verify session is active ✅
- [ ] **Step 7**: Access patient data ✅

**Success Criteria**: You should be able to retrieve patient FHIR data from Epic's sandbox using your access token.

---

## 📱 Using Browser for OAuth Testing

### Alternative Browser-Based Testing:

1. **Visit**: http://localhost:8000/docs
2. **Find**: `/fhir/authorize/{client_id}` endpoint
3. **Execute**: With your client ID
4. **Copy**: The authorization_url from response
5. **Open**: URL in new browser tab
6. **Login**: With Epic credentials
7. **Grant**: Access when prompted
8. **Note**: Session ID from redirect response

---

**🎉 You're all set! Start with Step 1 and work through the complete workflow.**
