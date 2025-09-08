# FHIR Integration Guide

This guide explains how to use the Epic FHIR integration endpoints in the PHA application.

## Overview

The FHIR integration follows Epic's OAuth 2.0 Standalone Launch flow, allowing users to authenticate and access patient data from Epic's FHIR sandbox.

## Configuration

The application is configured with the following Epic FHIR settings:

- **Client ID**: `50560479-b540-428a-9b34-a8c49f51f0c0`
- **Client Secret**: `Wui9fco0ArmvIvR/p9DPhXTMhPhpRDl0H19ABUBWHGx0ZOJWFUX4QnAQuCIlyx6BGRGAmT2/TAK5R4c757k2xg==`
- **Authorization URL**: `https://fhir.epic.com/Authorization/oauth2/authorize`
- **Token URL**: `https://fhir.epic.com/Authorization/oauth2/token`
- **Sandbox Base URL**: `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4`
- **Redirect URI**: `http://localhost:8000/fhir/callback`

## API Endpoints

### 1. Test Connection
**GET** `/fhir/test-connection`

Tests basic connectivity to the Epic FHIR server without authentication.

**Response:**
```json
{
  "status": "success",
  "status_code": 200,
  "server_info": {
    "base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
    "token_url": "https://fhir.epic.com/Authorization/oauth2/token"
  },
  "message": "FHIR server is reachable"
}
```

### 2. Start OAuth Flow
**GET** `/fhir/authorize`

Initiates the OAuth 2.0 authorization flow with Epic FHIR.

**Response:**
```json
{
  "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize?response_type=code&client_id=...",
  "state": "random_state_string",
  "instructions": "Redirect user to the authorization_url to complete Epic login"
}
```

**Usage:**
1. Call this endpoint to get the authorization URL
2. Redirect the user to the `authorization_url` in their browser
3. User will login with Epic credentials (sandbox test credentials)
4. User will be redirected back to the callback endpoint

### 3. OAuth Callback
**GET** `/fhir/callback?code={auth_code}&state={state}`

Handles the OAuth callback from Epic and exchanges the authorization code for an access token.

**Response:**
```json
{
  "message": "Successfully connected to Epic FHIR",
  "session_id": "random_session_id",
  "patient_id": "patient_fhir_id",
  "expires_in": 3600,
  "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read",
  "token_info": {
    "access_token": "eyJhbGciOiJSUzI1NiI...",
    "token_type": "bearer"
  }
}
```

### 4. Check Connection Status
**GET** `/fhir/status?session_id={session_id}`

Checks if the FHIR connection is still valid for a given session.

**Response:**
```json
{
  "connected": true,
  "patient_id": "patient_fhir_id",
  "expires_at": "2025-09-08T12:00:00Z",
  "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read"
}
```

### 5. Get Patient Data
**GET** `/fhir/patient/{patient_id}?session_id={session_id}`

Retrieves patient data from Epic FHIR using the stored access token.

**Response:**
Returns the FHIR Patient resource in JSON format.

### 6. Disconnect
**DELETE** `/fhir/disconnect?session_id={session_id}`

Disconnects from Epic FHIR by removing stored tokens.

**Response:**
```json
{
  "message": "Successfully disconnected from Epic FHIR"
}
```

### 7. Get FHIR Metadata
**GET** `/fhir/metadata`

Retrieves the FHIR server's capability statement/metadata.

## Epic Sandbox Test Credentials

For testing in the Epic sandbox, you can use these test credentials:
- **Username**: `fhiruser`
- **Password**: `epicepic1`

## OAuth 2.0 Flow Step-by-Step

1. **User starts authentication**: Call `/fhir/authorize` to get authorization URL
2. **User gets redirected to Epic**: Browser redirects to Epic's login page
3. **Hospital staff logs in**: User enters Epic sandbox credentials
4. **Epic redirects back**: Epic calls your `/fhir/callback` endpoint with authorization code
5. **Exchange code for token**: Your app automatically exchanges the code for an access token
6. **Access FHIR resources**: Use the session_id to make authenticated FHIR API calls

## Security Features

- **State Parameter**: Used to prevent CSRF attacks
- **Token Expiration**: Tokens automatically expire and are cleaned up
- **Session Management**: Each user gets a unique session ID
- **Error Handling**: Comprehensive error handling for OAuth failures

## Example Usage Flow

1. **Test connection:**
   ```bash
   curl http://localhost:8000/fhir/test-connection
   ```

2. **Start OAuth flow:**
   ```bash
   curl http://localhost:8000/fhir/authorize
   ```

3. **Redirect user to authorization_url returned from step 2**

4. **User completes login and is redirected to callback (automatic)**

5. **Check status:**
   ```bash
   curl "http://localhost:8000/fhir/status?session_id=YOUR_SESSION_ID"
   ```

6. **Get patient data:**
   ```bash
   curl "http://localhost:8000/fhir/patient/PATIENT_ID?session_id=YOUR_SESSION_ID"
   ```

## Production Considerations

- Replace the redirect URI with your production domain
- Store tokens securely in a database instead of in-memory storage
- Implement refresh token handling for long-lived sessions
- Add rate limiting and monitoring
- Use HTTPS for all endpoints
- Implement proper logging and audit trails
