"""FHIR Client Configuration and Session models."""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from bson import ObjectId


class FhirClientConfig:
    """Model for storing FHIR client configurations."""
    
    def __init__(
        self,
        client_id: str,
        client_name: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        fhir_base_url: str,
        redirect_uri: str,
        scopes: str = "openid fhirUser Patient.read Patient.search Practitioner.read",
        environment: str = "sandbox",
        description: Optional[str] = None
    ):
        self._id = None
        self.client_id = client_id
        self.client_name = client_name
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.fhir_base_url = fhir_base_url
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.environment = environment
        self.description = description
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB document format."""
        data = {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "client_secret": self.client_secret,
            "authorization_url": self.authorization_url,
            "token_url": self.token_url,
            "fhir_base_url": self.fhir_base_url,
            "redirect_uri": self.redirect_uri,
            "scopes": self.scopes,
            "environment": self.environment,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
        if self._id:
            data["_id"] = self._id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FhirClientConfig":
        """Create instance from MongoDB document."""
        instance = cls(
            client_id=data["client_id"],
            client_name=data["client_name"],
            client_secret=data["client_secret"],
            authorization_url=data["authorization_url"],
            token_url=data["token_url"],
            fhir_base_url=data["fhir_base_url"],
            redirect_uri=data["redirect_uri"],
            scopes=data.get("scopes", "openid fhirUser Patient.read Patient.search Practitioner.read"),
            environment=data.get("environment", "sandbox"),
            description=data.get("description")
        )
        
        instance._id = data.get("_id")
        instance.created_at = data.get("created_at", datetime.now(timezone.utc))
        instance.updated_at = data.get("updated_at", datetime.now(timezone.utc))
        
        return instance


class FhirSession:
    """Model for storing active FHIR OAuth sessions."""
    
    def __init__(
        self,
        session_id: str,
        client_id: str,
        state: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        patient_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        scopes_granted: Optional[str] = None
    ):
        self._id = None
        self.session_id = session_id
        self.client_id = client_id
        self.state = state
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.patient_id = patient_id
        self.expires_at = expires_at
        self.scopes_granted = scopes_granted
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB document format."""
        data = {
            "session_id": self.session_id,
            "client_id": self.client_id,
            "state": self.state,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "patient_id": self.patient_id,
            "expires_at": self.expires_at,
            "scopes_granted": self.scopes_granted,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
        if self._id:
            data["_id"] = self._id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FhirSession":
        """Create instance from MongoDB document."""
        instance = cls(
            session_id=data["session_id"],
            client_id=data["client_id"],
            state=data["state"],
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            patient_id=data.get("patient_id"),
            expires_at=data.get("expires_at"),
            scopes_granted=data.get("scopes_granted")
        )
        
        instance._id = data.get("_id")
        instance.created_at = data.get("created_at", datetime.now(timezone.utc))
        instance.updated_at = data.get("updated_at", datetime.now(timezone.utc))
        
        return instance
    
    def is_expired(self) -> bool:
        """Check if the access token has expired."""
        if not self.expires_at:
            return True
        return datetime.now(timezone.utc) > self.expires_at
