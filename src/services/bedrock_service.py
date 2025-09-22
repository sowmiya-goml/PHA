"""Simplified Bedrock service for healthcare query generation using dynamic approach."""

import os
import json
import re
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Dict, Any, Optional

from core.config import settings
from services.dynamic_query_generator import DynamicQueryGenerator

class BedrockService:
    """Simplified service for Bedrock AI operations using dynamic query generation."""
    
    def __init__(self, db_manager):
        """Initialize BedrockService with database manager and dynamic query generator."""
        self.db_manager = db_manager
        self.query_generator = DynamicQueryGenerator()
    
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
            from services.connection_service import ConnectionService
            
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
            
            # Step 3: Prepare schema for dynamic query generator
            schema_dict = self._prepare_schema_dict(schema_result)
            
            # Step 4: Generate query using dynamic query generator
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
    
    def _prepare_schema_dict(self, schema_result) -> Dict[str, Any]:
        """Prepare schema dictionary for the dynamic query generator."""
        unified_schema = schema_result.unified_schema or {}
        
        # Ensure database_info is present
        if 'database_info' not in unified_schema:
            unified_schema['database_info'] = {
                'type': schema_result.database_type,
                'name': schema_result.database_name
            }
        
        return {
            "unified_schema": unified_schema,
            "database_type": schema_result.database_type,
            "database_name": schema_result.database_name
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
        
        # Define query type keywords
        query_type_mapping = {
            'comprehensive': ['comprehensive', 'complete', 'full', 'all'],
            'clinical': ['clinical', 'medical', 'diagnosis', 'medication', 'procedure', 'lab'],
            'billing': ['billing', 'financial', 'payment', 'insurance', 'claim'],
            'basic': ['basic', 'simple', 'demographic']
        }
        
        # Check for specific query type keywords
        for query_type, keywords in query_type_mapping.items():
            if any(keyword in request_lower for keyword in keywords):
                return query_type
        
        # Default to comprehensive for general requests
        return 'comprehensive'
    
    def _clean_query(self, query: str) -> str:
        """Clean and format the generated SQL query."""
        if not query:
            return ""
        
        # Remove markdown code blocks
        query = query.strip()
        if query.startswith('```sql'):
            query = query[6:]
        elif query.startswith('```'):
            query = query[3:]
        if query.endswith('```'):
            query = query[:-3]
        
        # Remove unwanted patterns
        unwanted_patterns = [
            r'--.*?\n',           # SQL comments
            r'/\*.*?\*/',         # Multi-line comments
            r'\n\s*\n\s*\n',     # Multiple empty lines
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
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Generate a simple SQL query to select all patients."
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