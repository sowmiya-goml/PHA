"""Custom query agent service for dynamic user queries."""

from typing import Dict, Any
from datetime import datetime
from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from services.connection_service import ConnectionService
from schemas.database_operations import QueryExecutionResponse
import json


class CustomQueryService:
    """Service for handling dynamic user queries with custom report generation."""
    
    def __init__(self, db_manager, bedrock_service: BedrockService, db_ops_service: DatabaseOperationService):
        self.db_manager = db_manager
        self.bedrock_service = bedrock_service
        self.db_ops_service = db_ops_service
    
    async def process_custom_query(self, connection_id: str, user_query: str) -> Dict[str, Any]:
        """
        Process a custom user query and generate a comprehensive report.
        
        Args:
            connection_id: Database connection ID
            user_query: Natural language query from user
            
        Returns:
            Dict containing generated report and metadata
        """
        try:
            # Step 1: Get database schema
            connection_service = ConnectionService(self.db_manager)
            schema_result = await connection_service.get_database_schema(connection_id)
            
            if not schema_result or schema_result.status != "success":
                return {
                    "status": "error",
                    "error": f"Failed to get schema: {schema_result.message if schema_result else 'No schema result'}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Step 2: Generate SQL query using Bedrock
            query_result = await self.bedrock_service.generate_healthcare_query(
                connection_id=connection_id,
                query_request=user_query,
                patient_id=None  # No specific patient for custom queries
            )
            
            if not query_result or query_result.get("status") == "error":
                return {
                    "status": "error",
                    "error": f"Failed to generate query: {query_result.get('error', 'Unknown error')}",
                    "timestamp": datetime.now().isoformat()
                }
            
            generated_query = query_result.get("query", "")
            
            # Step 3: Execute the generated query
            db_results = await self.db_ops_service.execute_query(
                connection_id=connection_id,
                query=generated_query,
                limit=1000  # Reasonable limit for custom queries
            )
            
            if not db_results or len(db_results) == 0:
                return {
                    "status": "success",
                    "generated_query": generated_query,
                    "data": [],
                    "report": "No data found for the given query.",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Step 4: Generate comprehensive report using the retrieved data
            first_result = db_results[0]
            report = await self._generate_custom_report(
                user_query=user_query,
                generated_query=generated_query,
                data=first_result.data,
                schema_info=schema_result
            )
            
            return {
                "status": "success",
                "user_query": user_query,
                "generated_query": generated_query,
                "data": first_result.data,
                "report": report,
                "records_count": first_result.row_count,
                "execution_time_ms": first_result.execution_time_ms,
                "database_info": {
                    "connection_id": connection_id,
                    "database_type": schema_result.database_type,
                    "database_name": schema_result.database_name
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Custom query processing failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_custom_report(
        self,
        user_query: str,
        generated_query: str,
        data: list,
        schema_info
    ) -> str:
        """Generate a custom report based on the query results."""
        try:
            # Format data for the LLM
            formatted_data = json.dumps(data, indent=2, default=str) if data else "No data available"
            
            # Create report generation prompt
            report_prompt = f"""You are an expert healthcare data analyst. Generate a comprehensive, professional report based on the following information:

**User Query:** {user_query}
**Generated SQL Query:** {generated_query}
**Retrieved Data:** {formatted_data}
**Database Type:** {schema_info.database_type}
**Database Name:** {schema_info.database_name}

Please create a detailed report that includes:

1. **Executive Summary**
   - Brief overview of what was requested and found
   - Key findings and insights

2. **Data Analysis**
   - Detailed analysis of the retrieved data
   - Patterns, trends, and notable observations
   - Statistical insights where applicable

3. **Technical Details**
   - Query execution summary
   - Data quality assessment
   - Any limitations or considerations

4. **Recommendations**
   - Actionable insights based on the data
   - Suggestions for further analysis if applicable

Format the report in clear, professional markdown with appropriate headings and sections. Make it informative and easy to understand for both technical and non-technical audiences."""

            # Call Bedrock to generate the report
            report_response = await self.bedrock_service._call_bedrock_api(report_prompt)
            
            if report_response.get("status") == "success":
                content = report_response.get("raw_response", {}).get('content', [])
                if content:
                    return content[0].get('text', 'Unable to generate report')
            
            return "Unable to generate comprehensive report"
            
        except Exception as e:
            return f"Error generating report: {str(e)}"