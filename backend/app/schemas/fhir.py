"""Pydantic schemas for FHIR API request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class FhirClientConfigCreate(BaseModel):
    """Schema for creating a new FHIR client configuration."""
    client_id: str = Field(..., min_length=1, max_length=100, description="FHIR client ID")
    client_name: str = Field(..., min_length=1, max_length=200, description="Human-readable client name")
    client_secret: str = Field(..., min_length=1, description="FHIR client secret")
    authorization_url: str = Field(..., description="OAuth2 authorization URL")
    token_url: str = Field(..., description="OAuth2 token URL")
    fhir_base_url: str = Field(..., description="FHIR server base URL")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    scopes: str = Field(
        default="openid fhirUser Patient.read Patient.search Practitioner.read",
        description="OAuth2 scopes to request"
    )
    environment: str = Field(default="sandbox", pattern="^(sandbox|production)$", description="Environment type")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")


class FhirClientConfigUpdate(BaseModel):
    """Schema for updating a FHIR client configuration."""
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    client_secret: Optional[str] = Field(None, min_length=1)
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    fhir_base_url: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: Optional[str] = None
    environment: Optional[str] = Field(None, pattern="^(sandbox|production)$")
    description: Optional[str] = Field(None, max_length=500)


class FhirClientConfigResponse(BaseModel):
    """Schema for FHIR client configuration responses."""
    client_id: str
    client_name: str
    authorization_url: str
    token_url: str
    fhir_base_url: str
    redirect_uri: str
    scopes: str
    environment: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Note: client_secret is intentionally excluded from response for security


class AuthorizeResponse(BaseModel):
    """Schema for OAuth authorization initiation response."""
    authorization_url: str = Field(..., description="URL to redirect user to for Epic login")
    state: str = Field(..., description="OAuth2 state parameter for security")
    session_id: str = Field(..., description="Session ID for tracking this OAuth flow")
    client_name: str = Field(..., description="Name of the FHIR client being used")
    instructions: str = Field(..., description="Instructions for the user")


class CallbackResponse(BaseModel):
    """Schema for OAuth callback response."""
    message: str
    session_id: str
    client_name: str
    patient_id: Optional[str] = None
    expires_in: Optional[int] = None
    scopes: Optional[str] = None
    token_info: Optional[dict] = None


class SessionStatusResponse(BaseModel):
    """Schema for FHIR session status response."""
    connected: bool
    session_id: str
    client_name: str
    patient_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: Optional[str] = None
    is_expired: bool


class FhirSessionResponse(BaseModel):
    """Schema for FHIR session information."""
    session_id: str
    client_id: str
    client_name: str
    patient_id: Optional[str]
    expires_at: Optional[datetime]
    scopes_granted: Optional[str]
    is_expired: bool
    created_at: datetime


class TestConnectionResponse(BaseModel):
    """Schema for FHIR connection test response."""
    status: str
    client_id: str
    client_name: str
    status_code: Optional[int] = None
    server_info: Optional[dict] = None
    message: str
    error_details: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: str
    status_code: int = 400
