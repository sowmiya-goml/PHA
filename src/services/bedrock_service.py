"""AWS Bedrock service for healthcare query generation using Claude AI."""

import os
import json
import re
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
from typing import Dict, Any, Optional

from core.config import settings
from prompt.prompts import BEDROCK_QUERY_GENERATION_PROMPT


class BedrockService:
    """AWS Bedrock service for AI-powered healthcare query generation."""
    
    def __init__(self, db_manager):
        """Initialize BedrockService with database manager."""
        self.db_manager = db_manager
        self.bedrock_client = None
        self._initialize_bedrock_client()
    
    def _initialize_bedrock_client(self):
        """Initialize AWS Bedrock client with proper configuration."""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=settings.AWS_DEFAULT_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Bedrock client: {e}")
            self.bedrock_client = None
    
    def _build_schema_description(self, tables_info: list, database_type: str) -> str:
        """Build a detailed schema description including columns for the prompt."""
        if not tables_info:
            return "No table information available."

        schema_lines = []
        schema_lines.append("DATABASE SCHEMA DETAILS:")
        schema_lines.append("=" * 80)

        for table in tables_info:
            table_name = table.get("name", "unknown")
            row_count = table.get("row_count", "unknown")
        
            # Get columns from the unified schema structure
            columns = table.get("columns", [])  # This is the correct key from unified schema
        
            schema_lines.append(f"\nTable: {table_name}")
            schema_lines.append(f"Rows: {row_count}")
            schema_lines.append("-" * 60)
        
            if not columns:
                schema_lines.append("  No column information available")
                continue
        
            # Add column headers
            schema_lines.append("  Columns:")
            schema_lines.append(f"  {'Column Name':<25} {'Data Type':<20} {'Nullable':<10} {'Key':<15}")
            schema_lines.append(f"  {'-'*25} {'-'*20} {'-'*10} {'-'*15}")
        
            # Add each column with detailed information
            for column in columns:  # These are dictionaries from unified schema
                column_name = column.get("name", "unknown")
                column_type = column.get("type", "unknown")
                is_nullable = column.get("nullable", True)
                is_primary = column.get("primary_key", False)
            
                # Format nullable status
                nullable_str = "YES" if is_nullable else "NO"
            
                # Format key information
                key_info = ""
                if is_primary:
                    key_info = "PRIMARY KEY"
                else:
                    key_info = ""
            
                # Format the column row
                schema_lines.append(f"  {column_name:<25} {column_type:<20} {nullable_str:<10} {key_info:<15}")
        
            # Add constraints if available
            constraints = table.get("constraints", {})
            if constraints:
                primary_keys = constraints.get("primary_keys", [])
                foreign_keys = constraints.get("foreign_keys", [])
                
                if primary_keys:
                    schema_lines.append(f"\n  Primary Keys: {', '.join(primary_keys)}")
                if foreign_keys:
                    schema_lines.append(f"  Foreign Keys: {', '.join(foreign_keys)}")
        
            schema_lines.append("")  # Empty line between tables

        # Add database-specific notes
        schema_lines.append("\nIMPORTANT NOTES:")
        schema_lines.append(f"- Database Type: {database_type}")
        schema_lines.append("- Use exact table and column names as shown above")
        schema_lines.append("- Pay attention to data types for proper query construction")
        schema_lines.append("- Consider nullable columns when writing WHERE clauses")
        schema_lines.append("- Use primary keys for JOIN operations when possible")

        return "\n".join(schema_lines)
    
    def _parse_query_type(self, query_request: str) -> str:
        """Parse the natural language query request to determine query type."""
        request_lower = query_request.lower()
        
        # Define query type keywords
        if any(word in request_lower for word in ['comprehensive', 'complete', 'full', 'all']):
            return 'comprehensive'
        elif any(word in request_lower for word in ['clinical', 'medical', 'diagnosis', 'medication', 'procedure', 'lab']):
            return 'clinical'
        elif any(word in request_lower for word in ['billing', 'financial', 'payment', 'insurance', 'claim']):
            return 'billing'
        elif any(word in request_lower for word in ['basic', 'simple', 'demographic']):
            return 'basic'
        
        # Default to comprehensive
        return 'comprehensive'
    
    async def generate_healthcare_query(
        self, 
        connection_id: str, 
        query_request: str, 
        patient_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate healthcare SQL query using AWS Bedrock Claude AI.
        
        Args:
            connection_id: Database connection ID
            query_request: Natural language query request
            patient_id: Optional patient ID for filtering
            **kwargs: Additional parameters (limit, query_type, etc.)
            
        Returns:
            Dictionary containing generated query and metadata
        """
        if not self.bedrock_client:
            return {
                "status": "error",
                "error": "AWS Bedrock client not initialized. Please check your AWS credentials.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
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
            
            # Step 2: Prepare prompt for Claude using prompts file
            prompt = self._create_bedrock_prompt(
                schema_result=schema_result,
                query_request=query_request,
                patient_id=patient_id,
                **kwargs
            )
            
            # Step 3: Call AWS Bedrock Claude API
            response = await self._call_bedrock_api(prompt)
            
            if response["status"] == "error":
                return response
            
            # Step 4: Extract and clean the generated query
            generated_query = self._extract_query_from_response(response["raw_response"])
            
            return {
                "status": "success",
                "query": self._clean_query(generated_query),
                "explanation": self._extract_explanation_from_response(response["raw_response"]),
                "metadata": {
                    "model_id": settings.BEDROCK_MODEL_ID,
                    "region": settings.AWS_DEFAULT_REGION,
                    "database_type": schema_result.database_type,
                    "patient_id": patient_id,
                    "query_request": query_request,
                    "schema_tables_count": len(schema_result.tables) if schema_result.tables else 0
                },
                "database_type": schema_result.database_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to generate healthcare query: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _create_bedrock_prompt(
        self,
        schema_result,
        query_request: str,
        patient_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Create a comprehensive prompt for AWS Bedrock Claude AI using prompts file."""
        # Extract key information
        database_type = schema_result.database_type
        unified_schema = schema_result.unified_schema
        tables_info = unified_schema.get("tables", [])
        
        # Build schema description using local method
        schema_description = self._build_schema_description(tables_info, database_type)
        
        # Get limit from kwargs
        limit = kwargs.get("limit", 100)
        
        # Format the prompt using the template from prompts file
        prompt = BEDROCK_QUERY_GENERATION_PROMPT.format(
            database_type=database_type,
            schema_description=schema_description,
            query_request=query_request,
            patient_id=patient_id,
            limit=limit
        )
        
        return prompt
    
    async def _call_bedrock_api(self, prompt: str) -> Dict[str, Any]:
        """Call AWS Bedrock Claude API with the prepared prompt."""
        try:
            # Prepare the request body for Claude
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.1,  # Low temperature for consistent results
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            # Call AWS Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=body,
                contentType='application/json'
            )
            
            # Parse response
            response_data = json.loads(response['body'].read().decode())
            
            return {
                "status": "success",
                "raw_response": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except NoCredentialsError:
            return {
                "status": "error",
                "error": "AWS credentials not found. Please configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.",
                "timestamp": datetime.utcnow().isoformat()
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            return {
                "status": "error",
                "error": f"AWS Bedrock API error ({error_code}): {error_message}",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Bedrock API call failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _extract_query_from_response(self, raw_response: Dict) -> str:
        """Extract SQL query from Claude's response."""
        try:
            content = raw_response.get('content', [])
            if content:
                text = content[0].get('text', '')
                
                # Extract SQL query from markdown code blocks
                sql_match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    return sql_match.group(1).strip()
                
                # Fallback: look for SELECT statements
                select_match = re.search(r'(SELECT\s+.*?;?)', text, re.DOTALL | re.IGNORECASE)
                if select_match:
                    return select_match.group(1).strip()
                
                return text.strip()
            
            return ""
        except Exception:
            return ""
    
    def _extract_explanation_from_response(self, raw_response: Dict) -> str:
        """Extract explanation from Claude's response."""
        try:
            content = raw_response.get('content', [])
            if content:
                text = content[0].get('text', '')
                
                # Look for explanation section
                explanation_match = re.search(r'\*\*Explanation:\*\*\s*(.*?)(?:\n\n|\*\*|$)', text, re.DOTALL)
                if explanation_match:
                    return explanation_match.group(1).strip()
                
                # Fallback: return text after SQL block
                sql_match = re.search(r'```sql.*?```\s*(.*)', text, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    return sql_match.group(1).strip()
                
                return "Query generated successfully."
            
            return "No explanation available."
        except Exception:
            return "No explanation available."
    
    def _clean_query(self, query: str) -> str:
        """Clean and format the generated SQL query."""
        if not query:
            return ""
        
        # Remove markdown artifacts
        query = query.strip()
        if query.startswith('```sql'):
            query = query[6:]
        elif query.startswith('```'):
            query = query[3:]
        if query.endswith('```'):
            query = query[:-3]
        
        # Remove comments and clean up
        query = re.sub(r'--.*?\n', '\n', query)  # Remove SQL comments
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)  # Remove multi-line comments
        query = re.sub(r'\n\s*\n\s*\n', '\n\n', query)  # Remove excessive empty lines
        query = re.sub(r'\s+', ' ', query)  # Normalize whitespace
        query = query.replace(' ;', ';')  # Fix semicolon spacing
        
        return query.strip()
    
    def test_bedrock_connection(self) -> Dict[str, Any]:
        """Test AWS Bedrock connection and model availability."""
        if not self.bedrock_client:
            return {
                "status": "error",
                "error": "Bedrock client not initialized. Please check AWS credentials.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # Test with a simple query
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Generate a simple SQL query to select all patients from a patients table."
                    }
                ]
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=body,
                contentType='application/json'
            )
            
            response_data = json.loads(response['body'].read().decode())
            
            return {
                "status": "success",
                "message": "AWS Bedrock connection successful",
                "model_id": settings.BEDROCK_MODEL_ID,
                "region": settings.AWS_DEFAULT_REGION,
                "test_response": response_data.get('content', [{}])[0].get('text', ''),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Bedrock connection test failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }