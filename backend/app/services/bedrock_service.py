"""Bedrock service for static connection management."""

import os
from datetime import datetime
from typing import Dict, Any
from bson import ObjectId

from app.core.config import settings
from app.models.connection import DatabaseConnection
from app.schemas.connection import DatabaseConnectionResponse


class BedrockService:
    """Service to manage static Bedrock connection."""
    
    BEDROCK_CONNECTION_ID = "bedrock_static_connection"
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self._ensure_bedrock_connection()
    
    def _ensure_bedrock_connection(self):
        """Ensure static Bedrock connection exists in database."""
        collection = self.db_manager.get_connections_collection()
        
        # Check if Bedrock connection already exists
        existing = collection.find_one({"connection_name": "Static Bedrock Connection"})
        if existing:
            return
        
        # Create static Bedrock connection
        bedrock_connection = DatabaseConnection(
            connection_name="Static Bedrock Connection",
            database_type="bedrock",
            aws_region=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            model_id=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3.5-sonnet-20240620-v1:0')
        )
        
        # Insert with custom ID for easy reference
        connection_doc = bedrock_connection.to_dict()
        connection_doc["_id"] = self.BEDROCK_CONNECTION_ID
        
        try:
            collection.insert_one(connection_doc)
            print("✅ Static Bedrock connection created successfully")
        except Exception as e:
            print(f"⚠️ Failed to create Bedrock connection: {e}")
    
    def get_bedrock_connection(self) -> Dict[str, Any]:
        """Get the static Bedrock connection."""
        collection = self.db_manager.get_connections_collection()
        return collection.find_one({"_id": self.BEDROCK_CONNECTION_ID})
    
    def get_bedrock_connection_response(self) -> DatabaseConnectionResponse:
        """Get Bedrock connection as response object."""
        connection_doc = self.get_bedrock_connection()
        if not connection_doc:
            raise RuntimeError("Bedrock connection not found")
        
        connection = DatabaseConnection.from_dict(connection_doc)
        return DatabaseConnectionResponse(
            id=str(connection._id),
            connection_name=connection.connection_name,
            database_type=connection.database_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=connection.password,
            arn=connection.arn,
            aws_region=connection.aws_region,
            model_id=connection.model_id,
            additional_notes=connection.additional_notes,
            created_at=connection.created_at,
            updated_at=connection.updated_at
        )
