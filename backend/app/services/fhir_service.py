"""FHIR service for handling OAuth flows and FHIR API operations."""

import httpx
import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode, parse_qs, urlparse

from app.models.fhir_client import FhirClientConfig, FhirSession
from app.db.session import DatabaseManager


class FhirService:
    """Service for FHIR client configuration management and OAuth flows."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.clients_collection = db_manager.get_database().fhir_clients
        self.sessions_collection = db_manager.get_database().fhir_sessions
    
    # CRUD Operations for FHIR Client Configurations
    
    async def create_client_config(self, client_data: dict) -> FhirClientConfig:
        """Create a new FHIR client configuration."""
        # Check if client_id already exists
        existing = await self.clients_collection.find_one({"client_id": client_data["client_id"]})
        if existing:
            raise ValueError(f"Client ID {client_data['client_id']} already exists")
        
        client_config = FhirClientConfig(**client_data)
        result = await self.clients_collection.insert_one(client_config.to_dict())
        client_config._id = result.inserted_id
        
        return client_config
    
    async def get_all_client_configs(self) -> List[FhirClientConfig]:
        """Get all FHIR client configurations."""
        cursor = self.clients_collection.find({})
        configs = []
        async for doc in cursor:
            configs.append(FhirClientConfig.from_dict(doc))
        return configs
    
    async def get_client_config(self, client_id: str) -> Optional[FhirClientConfig]:
        """Get a specific FHIR client configuration by client_id."""
        doc = await self.clients_collection.find_one({"client_id": client_id})
        if doc:
            return FhirClientConfig.from_dict(doc)
        return None
    
    async def update_client_config(self, client_id: str, update_data: dict) -> Optional[FhirClientConfig]:
        """Update a FHIR client configuration."""
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.clients_collection.update_one(
            {"client_id": client_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_client_config(client_id)
        return None
    
    async def delete_client_config(self, client_id: str) -> bool:
        """Delete a FHIR client configuration."""
        # Also delete any sessions for this client
        await self.sessions_collection.delete_many({"client_id": client_id})
        
        result = await self.clients_collection.delete_one({"client_id": client_id})
        return result.deleted_count > 0
    
    # OAuth Flow Operations
    
    async def start_oauth_flow(self, client_id: str) -> Dict[str, Any]:
        """Start OAuth2 authorization flow for a FHIR client."""
        client_config = await self.get_client_config(client_id)
        if not client_config:
            raise ValueError(f"Client ID {client_id} not found")
        
        # Generate session and state
        session_id = str(uuid.uuid4())
        state = secrets.token_urlsafe(32)
        
        # Create session record
        session = FhirSession(
            session_id=session_id,
            client_id=client_id,
            state=state
        )
        await self.sessions_collection.insert_one(session.to_dict())
        
        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": client_config.client_id,
            "redirect_uri": client_config.redirect_uri,
            "scope": client_config.scopes,
            "state": state,
            "aud": client_config.fhir_base_url
        }
        
        authorization_url = f"{client_config.authorization_url}?{urlencode(auth_params)}"
        
        return {
            "authorization_url": authorization_url,
            "state": state,
            "session_id": session_id,
            "client_name": client_config.client_name,
            "instructions": f"Redirect user to the authorization_url to complete {client_config.client_name} login"
        }
    
    async def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth2 callback and exchange code for tokens."""
        # Find session by state
        session_doc = await self.sessions_collection.find_one({"state": state})
        if not session_doc:
            raise ValueError("Invalid state parameter or session expired")
        
        session = FhirSession.from_dict(session_doc)
        
        # Get client configuration
        client_config = await self.get_client_config(session.client_id)
        if not client_config:
            raise ValueError("Client configuration not found")
        
        # Exchange code for tokens
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": client_config.redirect_uri,
            "client_id": client_config.client_id
        }
        
        # Add client_secret for confidential clients
        if client_config.client_secret:
            token_data["client_secret"] = client_config.client_secret
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                client_config.token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0
            )
            
            if response.status_code != 200:
                error_detail = f"Token exchange failed: {response.status_code} - {response.text}"
                raise ValueError(error_detail)
            
            token_response = response.json()
        
        # Extract token information
        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in", 3600)  # Default 1 hour
        patient_id = token_response.get("patient")
        scope = token_response.get("scope")
        
        # Update session with tokens
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        update_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "patient_id": patient_id,
            "expires_at": expires_at,
            "scopes_granted": scope,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.sessions_collection.update_one(
            {"session_id": session.session_id},
            {"$set": update_data}
        )
        
        return {
            "message": f"Successfully connected to {client_config.client_name}",
            "session_id": session.session_id,
            "client_name": client_config.client_name,
            "patient_id": patient_id,
            "expires_in": expires_in,
            "scopes": scope,
            "token_info": {
                "access_token": access_token[:50] + "..." if access_token else None,
                "token_type": "bearer"
            }
        }
    
    # Session Management
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a FHIR session."""
        session_doc = await self.sessions_collection.find_one({"session_id": session_id})
        if not session_doc:
            return None
        
        session = FhirSession.from_dict(session_doc)
        client_config = await self.get_client_config(session.client_id)
        
        if not client_config:
            return None
        
        return {
            "connected": session.access_token is not None and not session.is_expired(),
            "session_id": session.session_id,
            "client_name": client_config.client_name,
            "patient_id": session.patient_id,
            "expires_at": session.expires_at,
            "scopes": session.scopes_granted,
            "is_expired": session.is_expired()
        }
    
    async def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all active FHIR sessions."""
        cursor = self.sessions_collection.find({})
        sessions = []
        
        async for doc in cursor:
            session = FhirSession.from_dict(doc)
            client_config = await self.get_client_config(session.client_id)
            
            if client_config:
                sessions.append({
                    "session_id": session.session_id,
                    "client_id": session.client_id,
                    "client_name": client_config.client_name,
                    "patient_id": session.patient_id,
                    "expires_at": session.expires_at,
                    "scopes_granted": session.scopes_granted,
                    "is_expired": session.is_expired(),
                    "created_at": session.created_at
                })
        
        return sessions
    
    async def disconnect_session(self, session_id: str) -> bool:
        """Disconnect a FHIR session by removing stored tokens."""
        result = await self.sessions_collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0
    
    # FHIR API Operations
    
    async def get_patient_data(self, session_id: str, patient_id: str) -> Dict[str, Any]:
        """Get patient data using stored access token."""
        session_doc = await self.sessions_collection.find_one({"session_id": session_id})
        if not session_doc:
            raise ValueError("Session not found")
        
        session = FhirSession.from_dict(session_doc)
        if session.is_expired() or not session.access_token:
            raise ValueError("Session expired or no access token")
        
        client_config = await self.get_client_config(session.client_id)
        if not client_config:
            raise ValueError("Client configuration not found")
        
        # Make FHIR API request
        headers = {
            "Authorization": f"Bearer {session.access_token}",
            "Accept": "application/fhir+json"
        }
        
        url = f"{client_config.fhir_base_url}/Patient/{patient_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                error_detail = f"FHIR API request failed: {response.status_code} - {response.text}"
                raise ValueError(error_detail)
            
            return response.json()
    
    async def test_client_connection(self, client_id: str) -> Dict[str, Any]:
        """Test connection to FHIR server without authentication."""
        client_config = await self.get_client_config(client_id)
        if not client_config:
            raise ValueError(f"Client ID {client_id} not found")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test metadata endpoint (usually public)
                metadata_url = f"{client_config.fhir_base_url}/metadata"
                response = await client.get(metadata_url, timeout=10.0)
                
                return {
                    "status": "success" if response.status_code == 200 else "warning",
                    "client_id": client_id,
                    "client_name": client_config.client_name,
                    "status_code": response.status_code,
                    "server_info": {
                        "fhir_base_url": client_config.fhir_base_url,
                        "authorization_url": client_config.authorization_url,
                        "token_url": client_config.token_url,
                        "environment": client_config.environment
                    },
                    "message": f"FHIR server is reachable for {client_config.client_name}"
                }
        except httpx.RequestError as e:
            return {
                "status": "error",
                "client_id": client_id,
                "client_name": client_config.client_name,
                "status_code": None,
                "message": f"Failed to connect to FHIR server for {client_config.client_name}",
                "error_details": str(e)
            }
