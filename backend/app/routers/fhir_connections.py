"""FHIR connections router for Epic FHIR OAuth2 integration with CRUD operations."""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends, status

from app.schemas.fhir import (
    FhirClientConfigCreate, FhirClientConfigUpdate, FhirClientConfigResponse,
    AuthorizeResponse, CallbackResponse, SessionStatusResponse, FhirSessionResponse,
    TestConnectionResponse
)
from app.services.fhir_service import FhirService
from app.db.session import DatabaseManager, get_database_manager


router = APIRouter(
    prefix="/fhir",
    tags=["FHIR Integration"],
    responses={404: {"description": "Not found"}},
)


def get_fhir_service(db_manager: DatabaseManager = Depends(get_database_manager)) -> FhirService:
    """Dependency to get FHIR service instance."""
    return FhirService(db_manager)


# FHIR Client Configuration CRUD Endpoints

@router.post("/clients", response_model=FhirClientConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_fhir_client(
    client_data: FhirClientConfigCreate,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Create a new FHIR client configuration.
    
    This endpoint allows you to register a new FHIR client with Epic or other FHIR servers.
    You need to provide the client credentials and endpoint URLs.
    
    Example request body:
    {
        "client_id": "50560479-b540-428a-9b34-a8c49f51f0c0",
        "client_name": "Epic Sandbox Client",
        "client_secret": "your-client-secret",
        "authorization_url": "https://fhir.epic.com/Authorization/oauth2/authorize",
        "token_url": "https://fhir.epic.com/Authorization/oauth2/token",
        "fhir_base_url": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
        "redirect_uri": "http://localhost:8000/fhir/callback",
        "scopes": "openid fhirUser Patient.read Patient.search Practitioner.read",
        "environment": "sandbox",
        "description": "Epic FHIR sandbox client for testing"
    }
    """
    try:
        client_config = await fhir_service.create_client_config(client_data.dict())
        
        # Convert to response model (excluding client_secret for security)
        response_data = client_config.to_dict()
        response_data.pop('client_secret', None)  # Remove sensitive data
        response_data.pop('_id', None)  # Remove MongoDB internal ID
        
        return FhirClientConfigResponse(**response_data)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create client: {str(e)}")


@router.get("/clients", response_model=List[FhirClientConfigResponse])
async def list_fhir_clients(fhir_service: FhirService = Depends(get_fhir_service)):
    """Get all FHIR client configurations.
    
    Returns a list of all registered FHIR clients (client secrets are excluded for security).
    """
    try:
        clients = await fhir_service.get_all_client_configs()
        
        response_clients = []
        for client in clients:
            client_data = client.to_dict()
            client_data.pop('client_secret', None)  # Remove sensitive data
            client_data.pop('_id', None)  # Remove MongoDB internal ID
            response_clients.append(FhirClientConfigResponse(**client_data))
        
        return response_clients
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve clients: {str(e)}")


@router.get("/clients/{client_id}", response_model=FhirClientConfigResponse)
async def get_fhir_client(
    client_id: str,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Get a specific FHIR client configuration by client ID."""
    try:
        client_config = await fhir_service.get_client_config(client_id)
        
        if not client_config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client {client_id} not found")
        
        # Convert to response model (excluding client_secret for security)
        response_data = client_config.to_dict()
        response_data.pop('client_secret', None)  # Remove sensitive data
        response_data.pop('_id', None)  # Remove MongoDB internal ID
        
        return FhirClientConfigResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve client: {str(e)}")


@router.put("/clients/{client_id}", response_model=FhirClientConfigResponse)
async def update_fhir_client(
    client_id: str,
    update_data: FhirClientConfigUpdate,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Update a FHIR client configuration."""
    try:
        # Only include non-None fields in the update
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        
        updated_client = await fhir_service.update_client_config(client_id, update_dict)
        
        if not updated_client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client {client_id} not found")
        
        # Convert to response model (excluding client_secret for security)
        response_data = updated_client.to_dict()
        response_data.pop('client_secret', None)  # Remove sensitive data
        response_data.pop('_id', None)  # Remove MongoDB internal ID
        
        return FhirClientConfigResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update client: {str(e)}")


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fhir_client(
    client_id: str,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Delete a FHIR client configuration and all associated sessions."""
    try:
        deleted = await fhir_service.delete_client_config(client_id)
        
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client {client_id} not found")
        
        return  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete client: {str(e)}")


# OAuth Flow Endpoints

@router.get("/authorize/{client_id}", response_model=AuthorizeResponse)
async def start_oauth_flow(
    client_id: str,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Initiate OAuth2 authorization flow for a specific FHIR client.
    
    This endpoint starts the OAuth flow using the configuration of the specified client.
    The user will be redirected to the FHIR server's login page.
    
    Steps:
    1. Call this endpoint to get the authorization URL
    2. Redirect the user to that URL in their browser
    3. User logs in with Epic/FHIR credentials
    4. User is redirected back to the callback endpoint automatically
    """
    try:
        auth_data = await fhir_service.start_oauth_flow(client_id)
        return AuthorizeResponse(**auth_data)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start OAuth flow: {str(e)}")


@router.get("/callback", response_model=CallbackResponse)
async def oauth_callback(
    code: str = Query(..., description="Authorization code from FHIR server"),
    state: str = Query(..., description="State parameter for security validation"),
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Handle OAuth2 callback from FHIR server and exchange code for access token.
    
    This endpoint is called automatically by the FHIR server after user authentication.
    It exchanges the authorization code for an access token and creates a session.
    
    This is the redirect_uri endpoint that you register with Epic/FHIR server.
    """
    try:
        callback_data = await fhir_service.handle_oauth_callback(code, state)
        return CallbackResponse(**callback_data)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OAuth callback failed: {str(e)}")


# Session Management Endpoints

@router.get("/sessions", response_model=List[FhirSessionResponse])
async def list_fhir_sessions(fhir_service: FhirService = Depends(get_fhir_service)):
    """Get all active FHIR sessions."""
    try:
        sessions = await fhir_service.get_all_sessions()
        return [FhirSessionResponse(**session) for session in sessions]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve sessions: {str(e)}")


@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Check the status of a specific FHIR session."""
    try:
        status_data = await fhir_service.get_session_status(session_id)
        
        if not status_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        
        return SessionStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get session status: {str(e)}")


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_session(
    session_id: str,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Disconnect a FHIR session by removing stored tokens."""
    try:
        disconnected = await fhir_service.disconnect_session(session_id)
        
        if not disconnected:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        
        return  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to disconnect session: {str(e)}")


# FHIR API Data Endpoints

@router.get("/patient/{patient_id}")
async def get_patient_data(
    patient_id: str,
    session_id: str = Query(..., description="Session ID with valid access token"),
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Get patient data from FHIR server using stored access token."""
    try:
        patient_data = await fhir_service.get_patient_data(session_id, patient_id)
        return patient_data
        
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "expired" in str(e).lower() or "no access token" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve patient data: {str(e)}")


# Testing and Utility Endpoints

@router.get("/clients/{client_id}/test", response_model=TestConnectionResponse)
async def test_client_connection(
    client_id: str,
    fhir_service: FhirService = Depends(get_fhir_service)
):
    """Test connection to FHIR server for a specific client without authentication."""
    try:
        test_result = await fhir_service.test_client_connection(client_id)
        return TestConnectionResponse(**test_result)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Connection test failed: {str(e)}")


@router.get("/")
async def fhir_root():
    """FHIR integration root endpoint with API information."""
    return {
        "message": "FHIR Integration API",
        "version": "1.0.0",
        "description": "Epic FHIR OAuth2 integration with client configuration management",
        "endpoints": {
            "client_management": "/fhir/clients",
            "oauth_flow": "/fhir/authorize/{client_id}",
            "callback": "/fhir/callback",
            "sessions": "/fhir/sessions",
            "patient_data": "/fhir/patient/{patient_id}",
            "documentation": "/docs"
        },
        "workflow": [
            "1. POST /fhir/clients - Register FHIR client configuration",
            "2. GET /fhir/authorize/{client_id} - Start OAuth flow",
            "3. User completes login (automatic callback handling)",
            "4. Use session_id for API calls like /fhir/patient/{patient_id}"
        ],
        "epic_sandbox_credentials": {
            "username": "fhiruser",
            "password": "epicepic1"
        }
    }
