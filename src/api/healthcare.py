"""Healthcare query generation router with class-based structure."""

import re
from fastapi import APIRouter, Query, HTTPException, Depends
import json

from services.bedrock_service import BedrockService
from services.database_operation_service import DatabaseOperationService
from db.session import get_database_manager
from schemas.healthcare import HealthcareQueryResponse
from schemas.database_operations import QueryExecutionResponse


class HealthcareQueryController:
    """Controller class for healthcare query generation endpoints."""
    
    def __init__(self):
        """Initialize the healthcare query controller."""
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes for the healthcare query controller."""
        self.router.add_api_route(
            "/generate-query-by-connection",
            self.generate_query_by_connection,
            methods=["GET"],
            summary="Generate Query By Connection",
            description="Generate healthcare query using a database connection ID",
            response_model=HealthcareQueryResponse
        )
        
        self.router.add_api_route(
            "/generate-and-execute-query",
            self.generate_and_execute_query,
            methods=["GET"],
            summary="Generate and Execute Query",
            description="Generate healthcare query and execute it against the database to fetch actual data",
            response_model=QueryExecutionResponse
        )
    
    async def generate_query_by_connection(
        self,
        connection_id: str = Query(..., description="Database connection ID"),
        patient_id: str = Query(..., description="Patient ID for data extraction"),
        query_type: str = Query("comprehensive", description="Type of query: comprehensive, clinical, billing, basic"),
        db_manager = Depends(get_database_manager)
    ):
        """
        Generate healthcare query using a database connection ID.
        
        This endpoint automatically fetches the schema from the specified database connection
        and generates the appropriate healthcare query. No need to manually provide the schema.
        
        Query Types:
        - comprehensive: Full patient profile across all healthcare domains
        - clinical: Medical data focused (diagnoses, procedures, medications, labs, vitals)
        - billing: Financial data focused (bills, claims, payments, insurance)
        - basic: Essential patient information only (demographics, contacts)
        
        Example Usage:
        GET /healthcare/generate-query-by-connection?connection_id=507f1f77bcf86cd799439011&patient_id=687b0aca-ca63-4926-800b-90d5e92e5a0a&query_type=comprehensive
        """
        try:
            # Import here to avoid circular dependency
            from services.connection_service import ConnectionService
            
            connection_service = ConnectionService(db_manager)
            schema_result = await connection_service.get_database_schema(connection_id)
            
            if schema_result.status != "success":
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to retrieve schema: {schema_result.message}"
                )
            
            if not schema_result.unified_schema:
                raise HTTPException(
                    status_code=404,
                    detail="Unified schema not available for this database connection"
                )
            
            schema_dict = {
                "unified_schema": schema_result.unified_schema,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name
            }
            
            bedrock_service = BedrockService(db_manager)
            result = await bedrock_service.generate_healthcare_query(
                connection_id=connection_id,
                query_request=f"{query_type} healthcare query for patient {patient_id.strip()}",
                patient_id=patient_id.strip()
            )
            
            if result.get("status") == "error":
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            # Map the new response format to the expected schema
            response = {
                "generated_query": result.get("query", ""),
                "patient_id": patient_id.strip(),
                "query_type": query_type,
                "model_used": result.get("metadata", {}).get("model_id", "anthropic.claude-3.5-sonnet"),
                "schema_tables_count": schema_result.unified_schema.get("summary", {}).get("total_tables", 0),
                "status": result.get("status", "success"),
                "timestamp": result.get("timestamp", ""),
                "connection_info": {
                    "connection_id": connection_id,
                    "database_type": schema_result.database_type,
                    "database_name": schema_result.database_name,
                    "total_tables": schema_result.unified_schema.get("summary", {}).get("total_tables", 0)
                }
            }
            
            # Clean the query with regex
            response["generated_query"] = re.sub(r'\\"', '"', response["generated_query"]) 
            print(response["generated_query"])
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating query by connection: {str(e)}")

    async def generate_and_execute_query(
        self,
        connection_id: str = Query(..., description="Database connection ID"),
        patient_id: str = Query(..., description="Patient ID for data extraction"),
        query_type: str = Query("comprehensive", description="Type of query: comprehensive, clinical, billing, basic"),
        limit: int = Query(100, description="Maximum number of records to return (safety limit)"),
        db_manager = Depends(get_database_manager)
    ):
        """
        Generate healthcare query and execute it against the database to fetch actual data.
        
        This endpoint:
        1. Generates a healthcare query using AI (same as generate-query-by-connection)
        2. Validates the query for safety (read-only operations only)
        3. Executes the query against the actual database
        4. Returns both the generated query and the actual data
        
        Safety Features:
        - Only allows SELECT/FIND operations (read-only)
        - Validates queries to prevent SQL injection
        - Applies record limits to prevent excessive data retrieval
        - Timeout protection for long-running queries
        
        Query Types:
        - comprehensive: Full patient profile across all healthcare domains
        - clinical: Medical data focused (diagnoses, procedures, medications, labs, vitals)
        - billing: Financial data focused (bills, claims, payments, insurance)
        - basic: Essential patient information only (demographics, contacts)
        
        Example Usage:
        GET /healthcare/generate-and-execute-query?connection_id=507f1f77bcf86cd799439011&patient_id=687b0aca-ca63-4926-800b-90d5e92e5a0a&query_type=comprehensive&limit=50
        """
        try:
            # Import here to avoid circular dependency
            from services.connection_service import ConnectionService
            import time
            
            start_time = time.time()
            
            # Step 1: Generate the query (same as existing endpoint)
            connection_service = ConnectionService(db_manager)
            schema_result = await connection_service.get_database_schema(connection_id)
            
            if schema_result.status != "success":
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to retrieve schema: {schema_result.message}"
                )
            
            if not schema_result.unified_schema:
                raise HTTPException(
                    status_code=404,
                    detail="Unified schema not available for this database connection"
                )
            
            schema_dict = {
                "unified_schema": schema_result.unified_schema,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name
            }
            
            bedrock_service = BedrockService(db_manager)
            query_result = await bedrock_service.generate_healthcare_query(
                connection_id=connection_id,
                query_request=f"{query_type} healthcare query for patient {patient_id.strip()}",
                patient_id=patient_id.strip()
            )
            
            if query_result.get("status") == "error":
                raise HTTPException(status_code=500, detail=query_result.get("error"))
            
            # Step 2: Execute the generated query
            execution_results = []
            execution_errors = []
            total_records = 0
            query_executed = False
            
            try:
                db_operation_service = DatabaseOperationService(db_manager)
                generated_query = query_result.get("query", "")
                
                if generated_query:
                    execution_results = await db_operation_service.execute_query(
                        connection_id=connection_id,
                        query=generated_query,
                        limit=limit
                    )
                    query_executed = True
                    total_records = sum(result.row_count for result in execution_results)
                else:
                    execution_errors.append("No query was generated to execute")
                    
            except Exception as e:
                execution_errors.append(f"Query execution failed: {str(e)}")
            
            total_execution_time = (time.time() - start_time) * 1000
            
            # Step 3: Build comprehensive response
            connection_info = {
                "connection_id": connection_id,
                "database_type": schema_result.database_type,
                "database_name": schema_result.database_name,
                "total_tables": schema_result.unified_schema.get("summary", {}).get("total_tables", 0)
            }
            
            response = QueryExecutionResponse(
                # Query generation info (from existing functionality)
                generated_query=query_result.get("query", ""),
                patient_id=patient_id,
                query_type=query_type,
                model_used=query_result.get("metadata", {}).get("model_id", "anthropic.claude-3.5-sonnet"),
                schema_tables_count=schema_result.unified_schema.get("summary", {}).get("total_tables", 0),
                status="success" if not execution_errors else "partial_success",
                timestamp=query_result.get("timestamp", ""),
                connection_info=connection_info,
                
                # Query execution results (new functionality)
                query_executed=query_executed,
                execution_results=execution_results if execution_results else None,
                total_records_found=total_records if query_executed else None,
                total_execution_time_ms=total_execution_time,
                execution_errors=execution_errors if execution_errors else None
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in generate and execute query: {str(e)}")


# Create controller instance and get router
healthcare_controller = HealthcareQueryController()
router = healthcare_controller.router
