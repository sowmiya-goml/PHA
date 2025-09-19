"""Simplified Bedrock service for healthcare query generation using dynamic approach."""

import os
import json
import re
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Dict, Any, Optional, Union
from bson import ObjectId

from pha.core.config import settings
from pha.models.connection import DatabaseConnection
from pha.schemas.connection import DatabaseConnectionResponse
from pha.services.dynamic_query_generator import DynamicQueryGenerator


class BedrockService:
    """Simplified service for Bedrock AI operations using dynamic query generation."""
    
    BEDROCK_CONNECTION_ID = "bedrock_static_connection"
    
    def __init__(self, db_manager):
        """Initialize BedrockService with database manager and dynamic query generator."""
        self.db_manager = db_manager
        self._ensure_bedrock_connection()
        
        # Initialize dynamic query generator
        self.query_generator = DynamicQueryGenerator()
    
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
            connection_string=f"bedrock://{os.getenv('AWS_DEFAULT_REGION', 'us-east-1')}",
            additional_notes=f"Bedrock AI service - Model: {os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3.5-sonnet-20240620-v1:0')}"
        )
        
        # Insert with custom ID for easy reference
        connection_doc = bedrock_connection.to_dict()
        connection_doc["_id"] = self.BEDROCK_CONNECTION_ID
        connection_doc["aws_region"] = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        connection_doc["model_id"] = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3.5-sonnet-20240620-v1:0')
        
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
            connection_string=connection.connection_string,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password="*" * len(connection.password) if connection.password else None,
            additional_notes=connection.additional_notes,
            created_at=connection.created_at,
            updated_at=connection.updated_at
        )
    
    async def generate_healthcare_query(
        self, 
        connection_id: str, 
        query_request: str, 
        patient_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate healthcare SQL query using dynamic query generation approach.
        
        Args:
            connection_id: Database connection ID
            query_request: Natural language query request (will be parsed for query_type)
            patient_id: Optional patient ID for filtering
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing generated query and metadata
        """
        try:
            # Import here to avoid circular dependency
            from pha.services.connection_service import ConnectionService
            
            # Step 1: Get database schema
            connection_service = ConnectionService(self.db_manager)
            schema_result = await connection_service.get_database_schema(connection_id)
            
            if schema_result.status != "success":
                return {
                    "status": "error",
                    "error": f"Failed to retrieve schema: {schema_result.message}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if not schema_result.unified_schema:
                return {
                    "status": "error",
                    "error": "Unified schema not available for this database connection",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Step 2: Parse query_request to determine query_type
            query_type = self._parse_query_type(query_request)
            
            # Step 3: Prepare schema dict for dynamic query generator
            # The generator expects database info inside unified_schema.database_info
            unified_schema = schema_result.unified_schema or {}
            if 'database_info' not in unified_schema:
                unified_schema['database_info'] = {
                    'type': schema_result.database_type,
                    'name': schema_result.database_name
                }
            
            schema_dict = {
                "unified_schema": unified_schema,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name
            }
            
            # Step 4: Use the dynamic query generator
            result = self.query_generator.generate_healthcare_query(
                schema=schema_dict,
                patient_id=patient_id or "all",
                query_type=query_type,
                limit=kwargs.get('limit', 100)
            )
            
            return {
                "status": "success",
                "query": self._clean_query(result.get("generated_query", "")),
                "explanation": result.get("explanation", ""),
                "metadata": result.get("metadata", {}),
                "database_type": result.get("database_type", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to generate healthcare query: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _parse_query_type(self, query_request: str) -> str:
        """
        Parse the natural language query request to determine query type.
        
        Args:
            query_request: Natural language query request
            
        Returns:
            Query type string: 'comprehensive', 'clinical', 'billing', or 'basic'
        """
        request_lower = query_request.lower()
        
        # Look for specific query type keywords
        if any(word in request_lower for word in ['comprehensive', 'complete', 'full', 'all']):
            return 'comprehensive'
        elif any(word in request_lower for word in ['clinical', 'medical', 'diagnosis', 'medication', 'procedure', 'lab']):
            return 'clinical'
        elif any(word in request_lower for word in ['billing', 'financial', 'payment', 'insurance', 'claim']):
            return 'billing'
        elif any(word in request_lower for word in ['basic', 'simple', 'demographic']):
            return 'basic'
        else:
            # Default to comprehensive for general requests
            return 'comprehensive'
    
    def _clean_query(self, query: str) -> str:
        """Clean and format the generated SQL query."""
        if not query:
            return ""
        
        # Remove markdown code blocks and extra whitespace
        query = query.strip()
        
        # Remove markdown SQL code blocks
        if query.startswith('```sql'):
            query = query[6:]
        if query.startswith('```'):
            query = query[3:]
        if query.endswith('```'):
            query = query[:-3]
        
        # Clean up extra whitespace
        query = query.strip()
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'--.*?\n',  # SQL comments
            r'/\*.*?\*/',  # Multi-line comments
            r'\n\s*\n\s*\n',  # Multiple empty lines
        ]
        
        for pattern in unwanted_patterns:
            query = re.sub(pattern, '\n', query, flags=re.DOTALL)
        
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query)
        query = query.replace(' ;', ';')
        
        return query.strip()

    def test_bedrock_connection(self) -> Dict[str, Any]:
        """Test Bedrock AI connection and model availability."""
        try:
            # Initialize AWS Bedrock client
            bedrock = boto3.client(
                'bedrock-runtime',
                region_name=settings.AWS_DEFAULT_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            
            # Test with a simple query
            test_prompt = "Generate a simple SQL query to select all patients."
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ]
            })
            
            response = bedrock.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=body,
                contentType='application/json'
            )
            
            response_data = json.loads(response['body'].read().decode())
            
            return {
                "status": "success",
                "message": "Bedrock connection successful",
                "model_id": settings.BEDROCK_MODEL_ID,
                "region": settings.AWS_DEFAULT_REGION,
                "test_response": response_data.get('content', [{}])[0].get('text', ''),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Bedrock connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }


# Keep for backwards compatibility - alias to main class
BedrockHealthcareQueryService = BedrockService
